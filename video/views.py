from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from profiles.permissions import can_view

from .forms import VideoUploadForm
from .models import Video

User = get_user_model()


@login_required
def my_videos(request):
    return user_videos(request, request.user.id)


@login_required
def user_videos(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if not can_view(request.user, user, user.profile.privacy_video):
        return render(request, 'profiles/denied.html', {
            'pageuser': user,
            'message': 'Видеозаписи этого пользователя скрыты настройками приватности.',
        }, status=403)
    videos = Video.objects.filter(owner=user)
    return render(request, 'video/list.html', {
        'section': 'video' if user.id == request.user.id else None,
        'pageuser': user,
        'is_me': user.id == request.user.id,
        'videos': videos,
    })


@login_required
def view_video(request, video_id):
    video = get_object_or_404(Video.objects.select_related('owner'), pk=video_id)
    if not can_view(request.user, video.owner, video.owner.profile.privacy_video):
        return render(request, 'profiles/denied.html', {
            'pageuser': video.owner,
            'message': 'Видеозапись скрыта настройками приватности.',
        }, status=403)
    return render(request, 'video/view.html', {
        'section': 'video' if video.owner_id == request.user.id else None,
        'video': video,
        'is_owner': video.owner_id == request.user.id,
    })


@login_required
def upload(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.owner = request.user
            video.save()
            messages.success(request, 'Видеозапись загружена.')
            return redirect('video:view', video_id=video.id)
    else:
        form = VideoUploadForm()
    return render(request, 'video/upload.html', {
        'section': 'video',
        'form': form,
    })


@login_required
@require_POST
def delete_video(request, video_id):
    video = get_object_or_404(Video, pk=video_id, owner=request.user)
    video.delete()
    messages.info(request, 'Видеозапись удалена.')
    return redirect('video:my_videos')
