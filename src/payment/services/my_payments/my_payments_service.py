from django.core.paginator import Paginator, Page

from src.payment.models import Spending
from src.user.models import User


class MyPaymentsService:
    PER_PAGE = 25

    def get_my_spendings(self, user: User, current_page: int) -> Page[Spending]:
        spendings = Spending.objects.order_by('-id').select_related('by_user').select_related('on_user')

        if user.is_regular_user():
            spendings = spendings.filter(by_user=user)

        if user.is_creator():
            spendings = spendings.filter(on_user=user)

        paginator = Paginator(object_list=spendings, per_page=self.PER_PAGE)
        page = paginator.page(current_page)

        return page
