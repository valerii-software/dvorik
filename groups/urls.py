from django.urls import path

from . import views

app_name = 'groups'

urlpatterns = [
    path('', views.my_groups, name='my_groups'),
    path('all/', views.all_groups, name='all_groups'),
    path('new/', views.create_group, name='create_group'),
    path('user/<int:user_id>/', views.user_groups, name='user_groups'),
    path('<int:group_id>/', views.view, name='view'),
    path('<int:group_id>/edit/', views.edit_group, name='edit_group'),
    path('<int:group_id>/delete/', views.delete_group, name='delete_group'),
    path('<int:group_id>/join/', views.join, name='join'),
    path('<int:group_id>/leave/', views.leave, name='leave'),
    path('<int:group_id>/members/', views.members, name='members'),
]
