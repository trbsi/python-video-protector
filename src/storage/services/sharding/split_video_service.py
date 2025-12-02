import json
import os.path
import subprocess
from pathlib import Path

from protectapp import settings
from src.media.models import Media
from src.storage.services.sharding.shard_metadata_value_object import ShardMetadataValueObject
from src.storage.services.sharding.video_metadata_value_object import VideoMetadataValueObject


class SplitVideoService:
    def split_video_by_seconds(
            self,
            media: Media,
            local_file_path: str,
            seconds_per_video: int = 10
    ) -> VideoMetadataValueObject:
        output_dir = os.path.join(settings.MEDIA_ROOT, 'temp', str(media.id))
        input_path = Path(local_file_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get video duration
        video_duration = self._get_video_duration(local_file_path)

        # Split video
        self._split_video(output_dir, input_path, seconds_per_video)

        # Get codec string
        codec_string = self._get_mp4_codec_string(local_file_path)

        # Collect shards
        shards = sorted(output_dir.glob("shard_*.mp4"))
        number_of_shards = len(shards)

        meta = []
        for idx, shard in enumerate(shards):
            duration = seconds_per_video
            # Because last shard can have smaller duration
            if idx == number_of_shards - 1:
                tmp_duration = video_duration - idx * seconds_per_video
                if tmp_duration > 0:
                    duration = tmp_duration

            meta.append(
                ShardMetadataValueObject(
                    file=shard,
                    start_time=idx * seconds_per_video,
                    duration=duration
                ))

        return VideoMetadataValueObject(
            shards_metadata=meta,
            video_duration_in_seconds=video_duration,
            codec_string=codec_string
        )

    def _split_video(self, output_dir: Path, input_path: Path, seconds_per_video: int) -> None:
        # Example: output_000.mp4, output_001.mp4, ...
        output_pattern = str(f"{output_dir}/shard_%03d.mp4")

        cmd = [
            "ffmpeg",
            "-i", str(input_path),
            "-c", "copy",
            "-map", "0",
            "-f", "segment",
            "-segment_time", str(seconds_per_video),
            "-reset_timestamps", "1",
            "-force_key_frames", f"expr:gte(t,n_forced*{seconds_per_video})",
            output_pattern
        ]

        subprocess.run(cmd, check=True)

    def _get_video_duration(self, local_file_path: str) -> int:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "json",
            local_file_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        return int(info["format"]["duration"])

    def _get_mp4_codec_string(self, video_path: str) -> str:
        """
        Return something like: video/mp4; codecs="avc1.4d401f, mp4a.40.2"
        """
        # Probe video stream
        cmd_video = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=codec_name,profile,level",
            "-of", "json",
            video_path
        ]
        video_info = json.loads(subprocess.check_output(cmd_video))["streams"][0]

        v_codec = video_info["codec_name"]

        # Convert profile + level into MSE-friendly avc1.xxxxxx
        #
        # H.264 format: avc1.{profile_idc}{constraint_set}{level_idc}
        # FFprobe gives level as integer like 31 -> hex 1f
        #
        # Good defaults if profile missing:
        profile_hex_map = {
            "Baseline": "42",
            "Main": "4D",
            "High": "64"
        }

        if v_codec == "h264":
            profile = video_info.get("profile", "Main")
            level = video_info.get("level", 31)

            profile_hex = profile_hex_map.get(profile, "4D")
            level_hex = f"{level:02x}"  # convert to 2-char hex
            video_codec = f"avc1.{profile_hex}00{level_hex}"
        else:
            video_codec = v_codec

        # Probe audio stream
        cmd_audio = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "a:0",
            "-show_entries", "stream=codec_name",
            "-of", "json",
            video_path
        ]

        try:
            audio_info = json.loads(subprocess.check_output(cmd_audio))["streams"][0]
            a_codec = audio_info["codec_name"]

            if a_codec == "aac":
                audio_codec = "mp4a.40.2"  # AAC LC (most common)
            else:
                audio_codec = a_codec
        except Exception:
            audio_codec = None

        if audio_codec:
            return f'video/mp4; codecs="{video_codec}, {audio_codec}"'
        else:
            return f'video/mp4; codecs="{video_codec}"'
