import random
from datetime import datetime
from pathlib import Path

from django.contrib.auth.models import Group
from faker import Faker

from database.seeders.media_data import media_list, thumbnail_list
from src.media.enums import MediaEnum
from src.media.models import Media
from src.user.enum import UserEnum


class MediaSeeder:
    @staticmethod
    def seed():
        fake = Faker()

        creator_groups = Group.objects.filter(name=UserEnum.ROLE_CREATOR.value).first()
        creators = creator_groups.user_set.all()

        for creator in creators:
            for i in range(10):
                rand_media = random.choice(media_list)
                random_thumbnail = random.choice(thumbnail_list)
                extension = Path(rand_media.get('file_path')).suffix
                file_type = 'video' if extension == '.mp4' else 'image'

                Media.objects.create(
                    user=creator,
                    file_metadata=rand_media,
                    shards_metadata=rand_media,
                    file_type=file_type,
                    file_trailer=rand_media if file_type == 'video' else None,
                    file_thumbnail=random_thumbnail if file_type == 'video' else None,
                    status=MediaEnum.STATUS_PAID.value,
                    description=fake.text(),
                    created_at=datetime.now(),
                    share_count=random.randint(1, 1000),
                    like_count=random.randint(1, 1000),
                    comment_count=random.randint(1, 1000),
                )
