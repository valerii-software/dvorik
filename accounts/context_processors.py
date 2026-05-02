from django.contrib.auth import get_user_model


def user_counter(request):
    User = get_user_model()
    return {'total_users': User.objects.count()}
