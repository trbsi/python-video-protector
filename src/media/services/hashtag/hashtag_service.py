import re as regex

from src.media.models import Media, Hashtag


class HashtagService:
    def save_hashtags(self, media: Media, description: str | None) -> None:
        if not description:
            return

        # r"#\w+" → '#' followed by one or more word characters (letters, digits, underscore)
        hashtags = regex.findall(r"#\w+", description)
        if not hashtags:
            return

        hashtag_ids = []
        for hashtag in hashtags:
            hashtag = hashtag.lower()
            record, created = Hashtag.objects.get_or_create(hashtag=hashtag)
            record.count = int(record.count) + 1
            record.save()
            hashtag_ids.append(record.id)

        media.hashtags.set(hashtag_ids)
