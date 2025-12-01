from pathlib import Path


class ShardMetadataValueObject:
    def __init__(
            self,
            file: Path,
            start_time: int,
            duration: int
    ):
        self.file = file
        self.start_time = start_time
        self.duration = duration
