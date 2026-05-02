from django.urls import path

from . import views

app_name = 'audio'

urlpatterns = [
    path('', views.my_audio, name='my_audio'),
    path('search/', views.search, name='search'),
    path('upload/', views.upload, name='upload'),
    path('user/<int:user_id>/', views.user_audio, name='user_audio'),
    path('add/<int:track_id>/', views.add_to_mine, name='add'),
    path('remove/<int:track_id>/', views.remove_from_mine, name='remove'),
    path('delete/<int:track_id>/', views.delete_track, name='delete'),
]
