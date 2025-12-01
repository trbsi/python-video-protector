import os.path
import subprocess
from pathlib import Path

from protectapp import settings
from src.media.models import Media
from src.storage.services.sharding.shard_metadata_value_object import ShardMetadataValueObject


class SplitVideoService:
    def split_video_by_seconds(
            self,
            media: Media,
            local_file_path: str,
            seconds_per_video: int = 10
    ) -> tuple[list[ShardMetadataValueObject], int]:
        output_dir = os.path.join(settings.MEDIA_ROOT, 'temp', str(media.id))
        input_path = Path(local_file_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Example: output_000.mp4, output_001.mp4, ...
        output_pattern = str(output_dir / "shard_%03d.mp4")

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

        # Collect shards
        shards = sorted(output_dir.glob("shard_*.mp4"))

        meta = []
        for idx, shard in enumerate(shards):
            meta.append(
                ShardMetadataValueObject(
                    file=shard,
                    start_time=idx * seconds_per_video,
                    duration=seconds_per_video,
                ))

        total_time_in_seconds = len(shards) * seconds_per_video

        return meta, total_time_in_seconds
