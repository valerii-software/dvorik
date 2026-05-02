from django.urls import path

from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('unread-count/', views.unread_count, name='unread_count'),
    path('open/<int:user_id>/', views.open_dialog, name='open'),
    path('chat/<int:dialog_id>/', views.open_chat, name='open_chat'),
    path('send/<int:dialog_id>/', views.send, name='send'),
    path('new-group/', views.create_group, name='create_group'),
    path('leave/<int:dialog_id>/', views.leave_chat, name='leave_chat'),
    path('chat/<int:dialog_id>/add/', views.add_members, name='add_members'),
    path('chat/<int:dialog_id>/remove/<int:user_id>/', views.remove_member, name='remove_member'),
]
