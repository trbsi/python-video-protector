from django.contrib.auth.models import AnonymousUser
from django.core.paginator import Paginator, Page
from django.db.models import QuerySet
from django.urls import reverse_lazy

from src.media.models import Media
from src.user.models import User


class LoadFeedService:
    PER_PAGE_FOLLOW = 10
    PER_PAGE_DISCOVER = 20
    FEED_TYPE_FOLLOW = 'follow'
    FEED_TYPE_DISCOVER = 'discover'

    def get_following_feed(self, page: int, user: User | AnonymousUser, filters: str | None) -> dict:
        # include_following_list = self._get_followings(user=user)
        return self._get_feed_items(
            current_page=page,
            user=user,
            include_following_list=[],
            filters=filters,
            feed_type=self.FEED_TYPE_FOLLOW,
            per_page=self.PER_PAGE_FOLLOW,
        )

    def get_discover_feed(self, page: int, user: User | AnonymousUser, filters: str | None) -> dict:
        # exclude_following_list = self._get_followings(user=user)
        return self._get_feed_items(
            current_page=page,
            user=user,
            exclude_following_list=[],
            filters=filters,
            feed_type=self.FEED_TYPE_DISCOVER,
            per_page=self.PER_PAGE_DISCOVER,
        )

    def _get_feed_items(
            self,
            current_page: int,
            user: User | AnonymousUser,
            feed_type: str,
            per_page: int,
            include_following_list: list | None = None,
            exclude_following_list: list | None = None,
            filters: str | None = None,
    ) -> dict:
        items: QuerySet[Media] = (
            Media.objects
            .select_related('user')
            .order_by('-created_at')
            .filter(is_approved=True)
        )

        if include_following_list and feed_type == self.FEED_TYPE_FOLLOW:
            items = items.filter(user_id__in=list(include_following_list))

        if exclude_following_list and feed_type == self.FEED_TYPE_DISCOVER:
            items = items.exclude(user_id__in=list(exclude_following_list))

        paginator = Paginator(object_list=items, per_page=per_page)
        page: Page = paginator.page(current_page)

        result = self._prepare_result(page)
        next_page = page.next_page_number() if page.has_next() else None

        return {'result': result, 'next_page': next_page}

    def _prepare_result(self, page: Page) -> list:
        result = []
        for item in page.object_list:
            result.append({
                'id': item.id,
                'type': item.file_type,
                'src': item.get_trailer_url(),
                'thumbnail': item.get_thumbnail_url(),
                'url': reverse_lazy('media.view_single_media', kwargs={'id': item.id}),
                'like_count': item.like_count,
                'comments_count': item.comment_count,
                'user': {
                    'id': item.user.id,
                    'username': item.user.username,
                    'avatar': item.user.get_profile_picture(),
                    'profile_url': reverse_lazy('user.profile', kwargs={'username': item.user.username}),
                }
            })

        return result
