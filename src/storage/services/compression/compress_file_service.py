import os
import subprocess

from PIL import Image


class CompressFileService:
    IMAGE_QUALITY = 70
    IMAGE_MAX_SIZE = (1280, 1280)

    VIDEO_CRF = 28
    VIDEO_PRESET = "veryfast"
    VIDEO_MAX_HEIGHT = 720

    def compress_image(self, path: str) -> None:
        image = Image.open(path)
        # Convert non-RGB (e.g. PNG with alpha) → RGB for JPEG
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        image.thumbnail(size=self.IMAGE_MAX_SIZE)
        image.save(path, format="WEBP", quality=self.IMAGE_QUALITY)

    def compress_video(self, input_path: str, output_path: str) -> None:
        """
        Compress a video using ffmpeg.

        Args:
            crf: Constant Rate Factor (lower = better quality, bigger file)
            preset: Speed/efficiency tradeoff ("ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "veryslow")
            max_height: Resize height (maintains aspect ratio)
        """
        input_path_size = os.path.getsize(input_path)

        command = [
            "ffmpeg", "-i", input_path,
            "-vf", f"scale=-2:{self.VIDEO_MAX_HEIGHT}",  # keep aspect ratio, limit height
            "-c:v", "libx264",
            "-preset", self.VIDEO_PRESET,
            "-crf", str(self.VIDEO_CRF),
            "-c:a", "aac",
            "-b:a", "128k",
            output_path
        ]
        subprocess.run(command, check=True)

        output_path_size = os.path.getsize(output_path)

        if output_path_size > input_path_size:
            os.replace(input_path, output_path)
