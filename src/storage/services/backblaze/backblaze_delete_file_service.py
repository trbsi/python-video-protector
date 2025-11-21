from src.storage.init_storage import init_remote_storage


class BackBlazeDeleteFileService:
    def delete_file(self, file_id: str, file_name: str) -> None:
        b2_api = init_remote_storage()
        b2_api.delete_file_version(file_id, file_name)
