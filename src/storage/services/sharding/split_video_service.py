import json
import os.path
import subprocess
from pathlib import Path

from protectapp import settings
from src.media.enums import MediaEnum
from src.media.models import Media
from src.storage.services.sharding.shard_metadata_value_object import ShardMetadataValueObject
from src.storage.services.sharding.video_metadata_value_object import VideoMetadataValueObject


class SplitVideoService:
    OUTPUT_FORMAT = 'webm'

    def split_video_by_seconds(
            self,
            media: Media,
            local_file_path: str,
            seconds_per_video: int = MediaEnum.SECONDS_PER_SHARD.value
    ) -> VideoMetadataValueObject:
        output_dir = os.path.join(settings.MEDIA_ROOT, 'temp', str(media.id))
        input_path = Path(local_file_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Get video duration
        video_duration = self._get_video_duration(local_file_path)

        # Split video
        # Get codec string
        if self.OUTPUT_FORMAT == 'mp4':
            self._split_video_mp4(output_dir, input_path, seconds_per_video)
            codec_string = self._get_codec_string_mp4(local_file_path)
            shard_pattern = "shard_*.mp4"
        elif self.OUTPUT_FORMAT == 'webm':
            self._split_video_webm(output_dir, input_path, seconds_per_video)
            codec_string = 'video/webm; codecs="vp8, vorbis"'
            shard_pattern = "shard_*.webm"

        # Collect shards
        shards = sorted(output_dir.glob(shard_pattern))
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
            seconds_per_shard=seconds_per_video,
            codec_string=codec_string
        )

    def _split_video_webm(self, output_dir, input_path, seconds_per_video):
        output_pattern = str(f"{output_dir}/shard_%03d.webm")
        subprocess.run([
            "ffmpeg",
            "-i", input_path,
            "-c:v", "libvpx",
            "-b:v", "1M",
            "-crf", "10",
            "-c:a", "libvorbis",
            "-b:a", "128k",
            "-f", "webm",
            "-cluster_time_limit", "10000",
            "-cluster_size_limit", "5000000",
            output_pattern
        ], check=True)

    def _split_video_mp4(self, output_dir: Path, input_path: Path, seconds_per_video: int) -> None:
        # Example: output_000.mp4, output_001.mp4, ...
        output_pattern = str(f"{output_dir}/shard_%03d.mp4")

        cmd = [
            "ffmpeg",
            "-i", str(input_path),
            "-c", "copy",
            "-map", "0",
            "-f", "segment",
            "-segment_time", str(seconds_per_video),
            "-segment_format", "mp4",
            "-reset_timestamps", "1",
            "-movflags", "frag_keyframe+empty_moov+default_base_moof",  # MSE compatibility
            "-avoid_negative_ts", "make_zero",
            "-flags", "+global_header",
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
        return int(float(info["format"]["duration"]))

    def _get_codec_string_mp4(self, video_path) -> str:
        """
        Get MSE-compatible codec string from video file
        Returns: 'video/mp4; codecs="avc1.640028, mp4a.40.2"'
        """
        # Get video codec details
        cmd_video = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams',
            '-select_streams', 'v:0',
            str(video_path)
        ]

        result = subprocess.run(cmd_video, capture_output=True, text=True)
        data = json.loads(result.stdout)

        video_stream = data['streams'][0] if data.get('streams') else {}

        # Get audio codec details if exists
        cmd_audio = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_streams',
            '-select_streams', 'a:0',
            str(video_path)
        ]

        audio_result = subprocess.run(cmd_audio, capture_output=True, text=True)
        audio_data = json.loads(audio_result.stdout)
        audio_stream = audio_data['streams'][0] if audio_data.get('streams') else None

        # Build codec string based on codec
        video_codec = video_stream.get('codec_name', '')
        profile = video_stream.get('profile', '')
        level = video_stream.get('level', 0)

        mime_codec = ''

        # For H.264/AVC
        if video_codec == 'h264':
            # Convert profile to avc1 format
            profile_map = {
                'baseline': '42E0',
                'main': '4D40',
                'high': '6400'
            }

            profile_hex = profile_map.get(profile.lower(), '42E0')  # Default to baseline

            # Convert level to hex (e.g., 31 -> 0x1F -> 1F)
            if level:
                level_hex = f"{int(float(level)):02X}"
            else:
                level_hex = "1F"  # Default level 3.1

            video_codec_str = f"avc1.{profile_hex}{level_hex}"

        # For H.265/HEVC
        elif video_codec == 'hevc':
            video_codec_str = 'hev1.1.6.L93.B0'

        # For VP9
        elif video_codec == 'vp9':
            video_codec_str = 'vp09.00.10.08'

        # For AV1
        elif video_codec == 'av1':
            video_codec_str = 'av01.0.04M.08'

        else:
            video_codec_str = video_codec

        # Add audio codec if exists
        if audio_stream:
            audio_codec = audio_stream.get('codec_name', '')

            if audio_codec == 'aac':
                audio_codec_str = 'mp4a.40.2'  # AAC-LC
            elif audio_codec == 'opus':
                audio_codec_str = 'opus'
            elif audio_codec == 'mp3':
                audio_codec_str = 'mp4a.6B'
            else:
                audio_codec_str = audio_codec

            mime_codec = f'video/mp4; codecs="{video_codec_str}, {audio_codec_str}"'
        else:
            mime_codec = f'video/mp4; codecs="{video_codec_str}"'

        return mime_codec
