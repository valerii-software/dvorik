from django.urls import path

from . import views

app_name = 'wall'

urlpatterns = [
    path('post/<int:owner_id>/', views.post, name='post'),
    path('post/group/<int:group_id>/', views.post_to_group, name='post_to_group'),
    path('delete/<int:post_id>/', views.delete_post, name='delete'),
    path('comment/<int:post_id>/', views.comment, name='comment'),
]
