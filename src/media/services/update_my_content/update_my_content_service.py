from django.db import transaction

from src.media.enums import MediaEnum
from src.media.models import Media
from src.media.services.hashtag.hashtag_service import HashtagService
from src.media.utils import replace_tags
from src.user.models import UserProfile, User
from src.user.tasks import task_delete_user_media


class UpdateMyContentService:
    def __init__(self, hashtag_service=None):
        self.hashtag_service = hashtag_service or HashtagService()

    def update_my_content(
            self,
            user: User,
            delete_list: list,
            ids: list,
            descriptions: list,
            unlockPrices: list,
    ):
        if delete_list:
            Media.objects.filter(user=user).filter(id__in=delete_list).update(status=MediaEnum.STATUS_DELETED.value)
            profile: UserProfile = user.profile
            profile.media_count = profile.media_count - len(delete_list)
            profile.save()
        else:
            for (index, id) in enumerate(ids):
                description = replace_tags(descriptions[index])
                unlockPrice = replace_tags(unlockPrices[index])
                media: Media = Media.objects.filter(user=user, id=id).first()
                if media:
                    media.description = description
                    media.unlock_price = unlockPrice
                    media.save()
                    self.hashtag_service.save_hashtags(media=media, description=description)

        transaction.on_commit(lambda: task_delete_user_media.delay(user_id=user.id))
