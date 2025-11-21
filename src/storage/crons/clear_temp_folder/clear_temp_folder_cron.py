from pathlib import Path

from django.utils import timezone

from protectapp import settings


class ClearTempFolderCron:
    def clear_temp_folder(self) -> None:
        directory = Path(f'{settings.BASE_DIR}/uploads/temp')
        now = timezone.now().timestamp()

        files = []
        for file in directory.iterdir():
            if file.is_file():
                files.append(file)

        for file in files:
            creation_time = file.stat().st_ctime
            # if file is older than 1 hour
            if now - creation_time > 3600:
                file.unlink()
