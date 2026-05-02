from django.urls import path

from . import views

app_name = 'profiles'

urlpatterns = [
    path('', views.my_page, name='my_page'),
    path('edit/', views.edit, name='edit'),
    path('<int:user_id>/', views.view_profile, name='view'),
]
