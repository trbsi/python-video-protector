from django.urls import path

from . import views

urlpatterns = [
    path('my-spending', views.my_spending, name='payment.my_spending'),
    path('list-packages', views.list_packages, name='payment.list_packages'),
    path('buy-package/<int:package_id>', views.buy_single_package, name='payment.buy_single_package'),
    path('payment-webhook', views.payment_webhook),

    path('api/balance', views.api_get_balance, name='payment.api.get_balance'),
    path('api/can-spend', views.api_can_spend),
]
