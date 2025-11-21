import subprocess
import uuid

from src.media.models import Media
from src.storage.services.remote_storage_service import RemoteStorageService
from src.storage.utils import remote_file_path_for_media


class TrailerService:

    def __init__(self, remote_storage_service: RemoteStorageService | None = None):
        self.remote_storage_service = remote_storage_service or RemoteStorageService()

    def make_trailer(
            self,
            media: Media,
            local_file_type: str,
            local_file_path: str,
            local_file_path_directory: str,
            clip_count: int,
            min_length: int = 7,
            max_length: int = 15,
            percentage: float | None = None,
            trailer_length: int | None = None,
    ):
        """
        Video Processing Overview:

        1. **Get video duration**:
           - Uses `ffprobe` to extract the total duration of the input video file.

        2. **Determine trailer length**:
           - Computes a target trailer length as a percentage of the original video duration.
           - Ensures the trailer length is within the given `min_length` and `max_length`.

        3. **Determine clip positions and length**:
           - Divides the trailer into `clip_count` equally spaced segments.
           - Each clip has a duration of `trailer_length / clip_count`.
           - Clip start positions are chosen so that clips are evenly distributed throughout the video.

        4. **Extract clips**:
           - Loops over each position and uses `ffmpeg` to extract a clip of the computed length.
           - Clips are stored temporarily in the same directory, with unique filenames.

        5. **Merge clips into a trailer**:
           - Builds a `filter_complex` string for FFmpeg `concat` filter to combine video and audio streams.
           - Uses FFmpeg to concatenate all the clips into a single output trailer file.

        6. **Output**:
           - The final trailer is saved as a new MP4 file with a unique UUID filename in the same directory.

        Summary:
        The code takes an input video, extracts evenly spaced short clips, and concatenates them into a shorter trailer video while preserving audio.

        :param input_file: Path to the input video file
        :param output_file: Path to the output trailer file
        :param clip_count: How many clips to extract
        :param min_length: Minimum trailer length in seconds
        :param max_length: Maximum trailer length in seconds
        :param percentage: Fraction of video duration to use for trailer
        :param trailer_length: Set your own fixed trailer length
        """

        # Get video duration with ffprobe
        command = [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            local_file_path
        ]
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            text=True,
            check=True
        )
        duration = float(result.stdout.strip())

        # Cap-based trailer length
        if not trailer_length:
            if not min_length or not max_length or not percentage:
                raise Exception('percentage, min_length and max_length are required if trailer length not set')
            target_length = duration * percentage
            trailer_length = max(min_length, min(max_length, target_length))
        else:
            trailer_length = min(trailer_length, duration)

        # Length of each clip
        clip_length = trailer_length / clip_count

        # Pick positions evenly spaced across the video
        positions = []
        # We want to place clip_count positions evenly spaced within "duration".
        # Example: if duration=10 and clip_count=3 → positions at 2.5, 5.0, 7.5
        for i in range(clip_count):
            # i starts at 0, so use (i + 1) to avoid starting at 0
            step_index = i + 1
            # Compute the position as a fraction of the total duration
            position = duration * step_index / (clip_count + 1)
            # Store the computed position
            positions.append(position)

        parts = []
        part_uuid = uuid.uuid4()
        for i, pos in enumerate(positions):
            start = max(pos - clip_length / 2, 0)
            part = f"{local_file_path_directory}/{part_uuid}_part_{i}.mp4"
            command = [
                "ffmpeg", "-y", "-ss", str(start), "-i", str(local_file_path),
                "-t", str(clip_length), "-c:v", "libx264", "-c:a", "aac",
                str(part)
            ]
            subprocess.run(command, check=True)
            parts.append(part)

        # Merge into final trailer
        command = ["ffmpeg", "-y"]

        # Add each part as an input
        for part in parts:
            command += ["-i", part]

        # Build the filter_complex string
        filter_parts = []
        for i in range(len(parts)):
            filter_parts.append(f"[{i}:v][{i}:a]")
        filter_complex = "".join(filter_parts) + f"concat=n={len(parts)}:v=1:a=1[outv][outa]"

        # Complete FFmpeg command
        output_trailer_file_path = f'{local_file_path_directory}/{uuid.uuid4()}.mp4'
        command += ["-filter_complex", filter_complex, "-map", "[outv]", "-map", "[outa]",
                    str(output_trailer_file_path)]

        subprocess.run(command, check=True)

        # upload to remote
        remote_file_path = remote_file_path_for_media(media, 'mp4', 'trailer')

        file_info = self.remote_storage_service.upload_file(
            local_file_type=local_file_type,
            local_file_path=output_trailer_file_path,
            remote_file_path=remote_file_path,
        )

        media.file_trailer = file_info
        media.save()

        return {
            'parts': parts,
            'output_trailer_file_path': output_trailer_file_path
        }
