from django.urls import path

from . import views

urlpatterns = [
    path('upload', views.upload, name='media.upload'),
    path('my-content', views.my_content, name='media.my_content'),
    path('update-my-media', views.update_my_media, name='media.update_my_media'),

    path('api/upload', views.api_upload, name='media.api.upload'),
    path('unlock', views.unlock, name='media.unlock'),
    path('api/record-views', views.record_views, name='media.api.record_views'),
    path('api/media', views.api_get_feed, name='media.api.get_media'),

]
