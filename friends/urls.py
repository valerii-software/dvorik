from django.urls import path

from . import views

app_name = 'friends'

urlpatterns = [
    path('', views.my_friends, name='my_friends'),
    path('user/<int:user_id>/', views.user_friends, name='user_friends'),
    path('requests/', views.requests_view, name='requests'),
    path('search/', views.search, name='search'),
    path('add/<int:user_id>/', views.add, name='add'),
    path('cancel/<int:user_id>/', views.cancel, name='cancel'),
    path('accept/<int:user_id>/', views.accept, name='accept'),
    path('reject/<int:user_id>/', views.reject, name='reject'),
    path('remove/<int:user_id>/', views.remove, name='remove'),
]
