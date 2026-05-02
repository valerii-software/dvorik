from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from profiles.permissions import can_view

from .forms import AudioUploadForm
from .models import AudioTrack, UserAudio

User = get_user_model()


@login_required
def my_audio(request):
    return user_audio(request, request.user.id)


@login_required
def user_audio(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if not can_view(request.user, user, user.profile.privacy_audio):
        return render(request, 'profiles/denied.html', {
            'pageuser': user,
            'message': 'Аудиозаписи этого пользователя скрыты настройками приватности.',
        }, status=403)
    items = UserAudio.objects.filter(user=user).select_related('track', 'track__uploader')
    my_track_ids = set(
        UserAudio.objects.filter(user=request.user).values_list('track_id', flat=True)
    )
    return render(request, 'audio/list.html', {
        'section': 'audio' if user.id == request.user.id else None,
        'pageuser': user,
        'is_me': user.id == request.user.id,
        'items': items,
        'my_track_ids': my_track_ids,
    })


@login_required
def search(request):
    q = request.GET.get('q', '').strip()
    results = AudioTrack.objects.none()
    if q:
        results = AudioTrack.objects.filter(
            Q(title__icontains=q) | Q(artist__icontains=q)
        ).select_related('uploader')[:50]
    my_track_ids = set(
        UserAudio.objects.filter(user=request.user).values_list('track_id', flat=True)
    )
    return render(request, 'audio/search.html', {
        'section': 'audio_search',
        'q': q,
        'results': results,
        'my_track_ids': my_track_ids,
    })


@login_required
def upload(request):
    if request.method == 'POST':
        form = AudioUploadForm(request.POST, request.FILES)
        if form.is_valid():
            track = form.save(commit=False)
            track.uploader = request.user
            track.save()
            UserAudio.objects.get_or_create(user=request.user, track=track)
            messages.success(request, 'Аудиозапись загружена.')
            return redirect('audio:my_audio')
    else:
        form = AudioUploadForm()
    return render(request, 'audio/upload.html', {
        'section': 'audio',
        'form': form,
    })


@login_required
@require_POST
def add_to_mine(request, track_id):
    track = get_object_or_404(AudioTrack, pk=track_id)
    UserAudio.objects.get_or_create(user=request.user, track=track)
    return redirect(request.META.get('HTTP_REFERER') or 'audio:my_audio')


@login_required
@require_POST
def remove_from_mine(request, track_id):
    UserAudio.objects.filter(user=request.user, track_id=track_id).delete()
    return redirect(request.META.get('HTTP_REFERER') or 'audio:my_audio')


@login_required
@require_POST
def delete_track(request, track_id):
    track = get_object_or_404(AudioTrack, pk=track_id, uploader=request.user)
    track.delete()
    messages.info(request, 'Аудиозапись удалена.')
    return redirect('audio:my_audio')
