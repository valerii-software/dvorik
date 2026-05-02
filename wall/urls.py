from django.urls import path

from . import views

app_name = 'wall'

urlpatterns = [
    path('post/<int:owner_id>/', views.post, name='post'),
    path('post/group/<int:group_id>/', views.post_to_group, name='post_to_group'),
    path('posts/user/<int:owner_id>/', views.posts_partial, name='posts_partial'),
    path('posts/group/<int:group_id>/', views.posts_partial_group, name='posts_partial_group'),
    path('delete/<int:post_id>/', views.delete_post, name='delete'),
    path('comment/<int:post_id>/', views.comment, name='comment'),
    path('graffiti/user/<int:owner_id>/', views.graffiti, name='graffiti_user'),
    path('graffiti/group/<int:group_id>/', views.graffiti, name='graffiti_group'),
    path('graffiti/save/user/<int:owner_id>/', views.save_graffiti_user, name='save_graffiti_user'),
    path('graffiti/save/group/<int:group_id>/', views.save_graffiti_group, name='save_graffiti_group'),
]
