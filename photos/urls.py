from django.urls import path

from . import views

app_name = 'photos'

urlpatterns = [
    path('', views.my_albums, name='my_albums'),
    path('with-me/', views.with_me, name='with_me'),
    path('user/<int:user_id>/', views.user_albums, name='user_albums'),
    path('album/new/', views.create_album, name='create_album'),
    path('album/<int:album_id>/', views.album_view, name='album'),
    path('album/<int:album_id>/edit/', views.edit_album, name='edit_album'),
    path('album/<int:album_id>/delete/', views.delete_album, name='delete_album'),
    path('album/<int:album_id>/upload/', views.upload, name='upload'),
    path('photo/<int:photo_id>/', views.photo_view, name='photo'),
    path('photo/<int:photo_id>/delete/', views.delete_photo, name='delete_photo'),
    path('photo/<int:photo_id>/cover/', views.set_cover, name='set_cover'),
    path('photo/<int:photo_id>/tag/', views.tag, name='tag'),
    path('photo/<int:photo_id>/comment/', views.comment, name='comment'),
    path('tag/<int:tag_id>/untag/', views.untag, name='untag'),
]
