from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from friends.models import Friendship
from wall.forms import WallPostForm
from wall.models import WallPost

from .forms import ProfileForm
from .models import Profile

User = get_user_model()


@login_required
def my_page(request):
    return view_profile(request, request.user.id)


@login_required
def view_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    Profile.objects.get_or_create(user=user)
    profile = user.profile
    is_me = user.id == request.user.id
    friend_state = Friendship.state_between(request.user, user) if not is_me else None
    friend_count = Friendship.friends_qs(user).count()
    friends_preview = Friendship.friends_qs(user)[:6]
    posts = WallPost.objects.filter(owner=user).select_related('author', 'author__profile')
    return render(request, 'profiles/view.html', {
        'section': 'profile' if is_me else None,
        'pageuser': user,
        'profile': profile,
        'is_me': is_me,
        'friend_state': friend_state,
        'friend_count': friend_count,
        'friends_preview': friends_preview,
        'posts': posts,
        'wall_form': WallPostForm(),
    })


@login_required
def edit(request):
    Profile.objects.get_or_create(user=request.user)
    profile = request.user.profile
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profiles:my_page')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'profiles/edit.html', {
        'section': 'edit',
        'form': form,
    })
