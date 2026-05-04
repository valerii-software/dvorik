from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from datetime import timedelta

from django.utils import timezone

from audio.models import UserAudio
from friends.models import Friendship
from groups.models import Group
from photos.models import Album, Photo
from video.models import Video
from wall.forms import WallPostForm
from wall.models import WallPost

from .forms import PrivacyForm, ProfileForm
from .models import Profile
from .permissions import visibility_flags

User = get_user_model()


def my_page(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    return redirect('profiles:view', user_id=request.user.id)


@login_required
def view_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    Profile.objects.get_or_create(user=user)
    profile = user.profile
    is_me = user.id == request.user.id

    flags = visibility_flags(request.user, user)

    if not flags['can_view_profile'] and not is_me:
        return render(request, 'profiles/closed.html', {
            'pageuser': user,
            'profile': profile,
            'friend_state': Friendship.state_between(request.user, user),
            'can_message': flags['can_message'],
        })

    friend_state = Friendship.state_between(request.user, user) if not is_me else None
    friends_qs = Friendship.friends_qs(user)
    friend_count = friends_qs.count()
    friends_preview = friends_qs[:6]
    online_threshold = timezone.now() - timedelta(minutes=5)
    friends_online = friends_qs.filter(profile__last_seen__gte=online_threshold)
    friends_online_count = friends_online.count()
    friends_online_preview = friends_online[:6]

    posts = WallPost.objects.none()
    if flags['can_view_wall']:
        posts = WallPost.objects.filter(owner=user).select_related('author', 'author__profile')

    album_count = photo_count = recent_photos = photos_with_user = None
    if flags['can_view_photos']:
        album_count = Album.objects.filter(owner=user).count()
        photo_count = Photo.objects.filter(album__owner=user).count()
        recent_photos = Photo.objects.filter(album__owner=user).order_by('-created_at')[:6]
        photos_with_user = Photo.objects.filter(tags__user=user).distinct().order_by('-created_at')[:6]

    user_groups = group_count = None
    if flags['can_view_groups']:
        groups_qs = Group.objects.filter(memberships__user=user).distinct()
        group_count = groups_qs.count()
        user_groups = groups_qs[:6]

    videos = video_count = None
    if flags['can_view_video']:
        videos_qs = Video.objects.filter(owner=user)
        video_count = videos_qs.count()
        videos = videos_qs[:4]

    audio_items = audio_count = None
    if flags['can_view_audio']:
        audio_qs = UserAudio.objects.filter(user=user).select_related('track')
        audio_count = audio_qs.count()
        audio_items = audio_qs[:5]

    return render(request, 'profiles/view.html', {
        'section': 'profile' if is_me else None,
        'pageuser': user,
        'profile': profile,
        'is_me': is_me,
        'friend_state': friend_state,
        'friend_count': friend_count,
        'friends_preview': friends_preview,
        'friends_online_count': friends_online_count,
        'friends_online_preview': friends_online_preview,
        'posts': posts,
        'wall_form': WallPostForm(),
        'album_count': album_count,
        'photo_count': photo_count,
        'recent_photos': recent_photos,
        'photos_with_user': photos_with_user,
        'user_groups': user_groups,
        'group_count': group_count,
        'videos': videos,
        'video_count': video_count,
        'audio_items': audio_items,
        'audio_count': audio_count,
        'completion': profile.completion() if is_me else None,
        **flags,
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


@login_required
def privacy(request):
    Profile.objects.get_or_create(user=request.user)
    profile = request.user.profile
    if request.method == 'POST':
        form = PrivacyForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Настройки приватности сохранены.')
            return redirect('profiles:privacy')
    else:
        form = PrivacyForm(instance=profile)
    return render(request, 'profiles/privacy.html', {
        'section': 'privacy',
        'form': form,
    })
