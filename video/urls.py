from django.urls import path

from . import views

app_name = 'video'

urlpatterns = [
    path('', views.my_videos, name='my_videos'),
    path('upload/', views.upload, name='upload'),
    path('user/<int:user_id>/', views.user_videos, name='user_videos'),
    path('<int:video_id>/', views.view_video, name='view'),
    path('<int:video_id>/delete/', views.delete_video, name='delete'),
    path('<int:video_id>/comment/', views.comment, name='comment'),
]
