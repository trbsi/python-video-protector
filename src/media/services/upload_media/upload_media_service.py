from django.core.files.uploadedfile import UploadedFile

from src.media.enums import MediaEnum
from src.media.models import Media
from src.media.services.hashtag.hashtag_service import HashtagService
from src.media.utils import replace_tags
from src.storage.services.local_storage_service import LocalStorageService
from src.storage.services.remote_storage_service import RemoteStorageService
from src.storage.utils import remote_file_path_for_media
from src.user.models import UserProfile, User


class UploadMediaService:
    def __init__(
            self,
            remote_storage_service: RemoteStorageService | None = None,
            local_storage_service: LocalStorageService | None = None,
            hashtag_service: HashtagService | None = None,
    ):
        self.remote_storage_service = remote_storage_service or RemoteStorageService()
        self.local_storage_service = local_storage_service or LocalStorageService()
        self.hashtag_service = hashtag_service or HashtagService()

    def upload_media(
            self,
            user: User,
            uploaded_file: UploadedFile,
            description: str,
            post_type: str
    ) -> None:
        """
        post_type: post_now|schedule
        """

        match post_type:
            case 'post_now':
                status = MediaEnum.STATUS_PENDING
            case 'schedule':
                status = MediaEnum.STATUS_SCHEDULE
            case _:
                status = MediaEnum.STATUS_PENDING

        description = replace_tags(description)
        media = Media.objects.create(
            file_info='',  # temporary
            file_type='video',  # temporary
            status=status.value,
            description=description,
            user=user,
        )

        # upload to temp local storage
        file_data = self.local_storage_service.temp_upload_file(uploaded_file=uploaded_file)
        file_type = file_data.get('file_type')
        remote_file_path = remote_file_path_for_media(media, file_data.get('extension'), file_type)
        local_file_path = file_data.get('local_file_path')

        remote_file_info: dict = self.remote_storage_service.upload_file(
            local_file_type=file_type,
            local_file_path=local_file_path,
            remote_file_path=remote_file_path
        )

        media.file_info = remote_file_info
        media.file_type = file_type
        media.save()

        profile: UserProfile = user.profile

        # save hashtags
        self.hashtag_service.save_hashtags(media=media, description=description)

        # Increase count
        profile.media_count += 1
        profile.save()

        # compress media
        # transaction.on_commit(
        #     lambda:
        #     task_process_media.delay(
        #         media_id=media.id,
        #         media_type=ProcessMediaTask.MEDIA_TYPE_MEDIA,
        #         local_file_path=local_file_path,
        #         create_thumbnail=True,
        #         create_trailer=True,
        #         should_compress_media=False,
        #         download_from_remote=False,
        #     )
        # )
