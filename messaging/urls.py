from django.urls import path

from . import views

app_name = 'messaging'

urlpatterns = [
    path('', views.inbox, name='inbox'),
    path('open/<int:user_id>/', views.open_dialog, name='open'),
    path('send/<int:dialog_id>/', views.send, name='send'),
]
