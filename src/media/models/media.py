from django.db import models

from protectapp import settings
from src.media.enums import MediaEnum
from src.media.models import Hashtag
from src.media.utils import load_tags
from src.user.models import User


class Media(models.Model):
    def get_upload_to_path(self, media, filename: str):
        return f'user_profile/{media.user_id}/{filename}'

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media_user')
    file_metadata = models.JSONField()
    shards_metadata = models.JSONField()
    file_thumbnail = models.JSONField(null=True, blank=True)
    file_trailer = models.JSONField(null=True, blank=True)
    file_type = models.CharField(max_length=20, choices=MediaEnum.file_types())
    status = models.CharField(max_length=20, choices=MediaEnum.statuses())
    description = models.TextField(null=True, blank=True)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    is_processed = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    unlock_price = models.DecimalField(decimal_places=2, max_digits=10, default=10)
    master_key = models.BinaryField(null=True, blank=True)  # wrapped master key (encrypted by root key)
    nonce = models.BinaryField(null=True, blank=True)  # wrap nonce, used to create wrapped master key
    created_at = models.DateTimeField(auto_now_add=True)
    hashtags = models.ManyToManyField(Hashtag, through='MediaHashtag', related_name='media_hashtags')

    objects = models.Manager()

    # objects_active = MediaManager()

    class Meta:
        indexes = [
            models.Index(fields=['status', 'is_approved', 'user_id'], name='idx_load_media_feed'),
        ]

    def get_file_url(self) -> str:
        return f'{settings.STORAGE_CDN_URL}/{self.file_metadata.get('file_path')}'

    def get_trailer_url(self) -> str | None:
        if self.is_image():
            return self.get_file_url()

        if self.file_trailer is None:
            return None

        return f'{settings.STORAGE_CDN_URL}/{self.file_trailer.get('file_path')}'

    def get_thumbnail_url(self) -> str | None:
        if self.is_image():
            return self.get_file_url()

        if self.file_thumbnail is None:
            return None
        return f'{settings.STORAGE_CDN_URL}/{self.file_thumbnail.get('file_path')}'

    def is_image(self):
        return self.file_type == MediaEnum.FILE_TYPE_IMAGE.value

    def is_video(self):
        return self.file_type == MediaEnum.FILE_TYPE_VIDEO.value

    def get_description(self) -> str:
        return load_tags(self.description)

    def codec_string(self) -> str:
        return self.file_metadata.get('codec_string')
