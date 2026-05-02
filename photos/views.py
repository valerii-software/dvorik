from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from friends.models import Friendship

from .forms import AlbumForm, PhotoCommentForm, PhotoUploadForm
from .models import Album, Photo, PhotoComment, PhotoTag

User = get_user_model()


@login_required
def my_albums(request):
    return user_albums(request, request.user.id)


@login_required
def user_albums(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    albums = Album.objects.filter(owner=user)
    return render(request, 'photos/albums.html', {
        'section': 'photos' if user.id == request.user.id else None,
        'pageuser': user,
        'is_me': user.id == request.user.id,
        'albums': albums,
    })


@login_required
def album_view(request, album_id):
    album = get_object_or_404(Album, pk=album_id)
    photos = album.photos.all()
    return render(request, 'photos/album.html', {
        'section': 'photos' if album.owner_id == request.user.id else None,
        'album': album,
        'photos': photos,
        'is_owner': album.owner_id == request.user.id,
    })


@login_required
def photo_view(request, photo_id):
    photo = get_object_or_404(Photo.objects.select_related('album', 'album__owner'), pk=photo_id)
    prev_id, next_id = photo.neighbours()
    is_owner = photo.album.owner_id == request.user.id
    friends = Friendship.friends_qs(request.user)
    tagged_ids = set(photo.tags.values_list('user_id', flat=True))
    taggable = [u for u in friends if u.id not in tagged_ids]
    return render(request, 'photos/photo.html', {
        'section': 'photos' if is_owner else None,
        'photo': photo,
        'album': photo.album,
        'prev_id': prev_id,
        'next_id': next_id,
        'is_owner': is_owner,
        'tags': photo.tags.select_related('user'),
        'taggable': taggable,
        'comment_form': PhotoCommentForm(),
    })


@login_required
def create_album(request):
    if request.method == 'POST':
        form = AlbumForm(request.POST)
        if form.is_valid():
            album = form.save(commit=False)
            album.owner = request.user
            album.save()
            return redirect('photos:upload', album_id=album.id)
    else:
        form = AlbumForm()
    return render(request, 'photos/album_form.html', {
        'section': 'photos',
        'form': form,
        'mode': 'create',
    })


@login_required
def edit_album(request, album_id):
    album = get_object_or_404(Album, pk=album_id, owner=request.user)
    if request.method == 'POST':
        form = AlbumForm(request.POST, instance=album)
        if form.is_valid():
            form.save()
            return redirect('photos:album', album_id=album.id)
    else:
        form = AlbumForm(instance=album)
    return render(request, 'photos/album_form.html', {
        'section': 'photos',
        'form': form,
        'album': album,
        'mode': 'edit',
    })


@login_required
@require_POST
def delete_album(request, album_id):
    album = get_object_or_404(Album, pk=album_id, owner=request.user)
    album.delete()
    messages.info(request, 'Альбом удалён.')
    return redirect('photos:my_albums')


@login_required
def upload(request, album_id):
    album = get_object_or_404(Album, pk=album_id, owner=request.user)
    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            files = form.cleaned_data['images']
            description = form.cleaned_data.get('description', '')
            for f in files:
                Photo.objects.create(
                    album=album, uploader=request.user,
                    image=f, description=description,
                )
            messages.success(request, f'Загружено фото: {len(files)}.')
            return redirect('photos:album', album_id=album.id)
    else:
        form = PhotoUploadForm()
    return render(request, 'photos/upload.html', {
        'section': 'photos',
        'album': album,
        'form': form,
    })


@login_required
@require_POST
def delete_photo(request, photo_id):
    photo = get_object_or_404(Photo, pk=photo_id)
    if photo.album.owner_id != request.user.id and photo.uploader_id != request.user.id:
        return redirect('photos:photo', photo_id=photo_id)
    album_id = photo.album_id
    photo.delete()
    return redirect('photos:album', album_id=album_id)


@login_required
@require_POST
def set_cover(request, photo_id):
    photo = get_object_or_404(Photo, pk=photo_id)
    if photo.album.owner_id != request.user.id:
        return redirect('photos:photo', photo_id=photo_id)
    photo.album.cover = photo
    photo.album.save(update_fields=['cover'])
    messages.success(request, 'Обложка обновлена.')
    return redirect('photos:photo', photo_id=photo_id)


@login_required
@require_POST
def tag(request, photo_id):
    photo = get_object_or_404(Photo, pk=photo_id)
    user_id = request.POST.get('user_id')
    if user_id:
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return redirect('photos:photo', photo_id=photo_id)
        PhotoTag.objects.get_or_create(
            photo=photo, user=user, defaults={'created_by': request.user},
        )
    return redirect('photos:photo', photo_id=photo_id)


@login_required
@require_POST
def untag(request, tag_id):
    t = get_object_or_404(PhotoTag, pk=tag_id)
    if request.user.id not in (t.user_id, t.created_by_id, t.photo.album.owner_id):
        return redirect('photos:photo', photo_id=t.photo_id)
    photo_id = t.photo_id
    t.delete()
    return redirect('photos:photo', photo_id=photo_id)


@login_required
@require_POST
def comment(request, photo_id):
    photo = get_object_or_404(Photo, pk=photo_id)
    form = PhotoCommentForm(request.POST)
    if form.is_valid():
        c = form.save(commit=False)
        c.photo = photo
        c.author = request.user
        c.save()
    return redirect('photos:photo', photo_id=photo_id)


@login_required
def with_me(request):
    tags = PhotoTag.objects.filter(user=request.user).select_related(
        'photo', 'photo__album', 'photo__album__owner',
    ).order_by('-created_at')
    return render(request, 'photos/with_me.html', {
        'section': 'with_me',
        'tags': tags,
    })
