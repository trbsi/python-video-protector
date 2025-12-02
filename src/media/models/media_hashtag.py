from django.db import models

from src.media.models.hashtag import Hashtag
from src.media.models.media import Media


class MediaHashtag(models.Model):
    id = models.BigAutoField(primary_key=True)
    media = models.ForeignKey(Media, on_delete=models.CASCADE)
    hashtag = models.ForeignKey(Hashtag, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['media', 'hashtag'], name='unique_media_hashtag'),
        ]
