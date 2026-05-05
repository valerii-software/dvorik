import base64
import binascii
import uuid

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from groups.models import Group
from profiles.permissions import can_view

from .forms import WallCommentForm, WallPostForm
from .models import WallPost

User = get_user_model()


def _can_delete(user, wp):
    if wp.author_id == user.id:
        return True
    if wp.owner_id == user.id:
        return True
    if wp.group_id and wp.group.owner_id == user.id:
        return True
    return False


def _redirect_to_target(wp):
    if wp.group_id:
        return redirect('groups:view', group_id=wp.group_id)
    return redirect('profiles:view', user_id=wp.owner_id)


@login_required
@require_POST
def post(request, owner_id):
    owner = get_object_or_404(User, pk=owner_id)
    if not can_view(request.user, owner, owner.profile.privacy_wall_post):
        return redirect('profiles:view', user_id=owner_id)
    form = WallPostForm(request.POST, request.FILES)
    if form.is_valid():
        wp = form.save(commit=False)
        wp.owner = owner
        wp.author = request.user
        wp.save()
        from messaging.consumers import push_notif_for_wall_post
        from .consumers import push_wall
        push_notif_for_wall_post(wp)
        push_wall(owner=owner)
    if request.headers.get('HX-Request'):
        posts = WallPost.objects.filter(owner=owner).select_related('author', 'author__profile')
        return render(request, 'wall/_posts.html', {'posts': posts, 'owner': owner})
    return redirect('profiles:view', user_id=owner_id)


@login_required
@require_POST
def post_to_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if not group.is_member(request.user) and group.owner_id != request.user.id:
        return redirect('groups:view', group_id=group.id)
    form = WallPostForm(request.POST, request.FILES)
    if form.is_valid():
        wp = form.save(commit=False)
        wp.group = group
        wp.author = request.user
        wp.save()
        from messaging.consumers import push_notif_for_wall_post
        from .consumers import push_wall
        push_notif_for_wall_post(wp)
        push_wall(group=group)
    if request.headers.get('HX-Request'):
        posts = WallPost.objects.filter(group=group).select_related('author', 'author__profile')
        return render(request, 'wall/_posts.html', {'posts': posts, 'group': group})
    return redirect('groups:view', group_id=group.id)


@login_required
@require_POST
def delete_post(request, post_id):
    wp = get_object_or_404(WallPost, pk=post_id)
    if not _can_delete(request.user, wp):
        return _redirect_to_target(wp)
    response = _redirect_to_target(wp)
    owner, group = wp.owner, wp.group
    wp.delete()
    from .consumers import push_wall
    if owner is not None:
        push_wall(owner=owner)
    elif group is not None:
        push_wall(group=group)
    return response


@login_required
def graffiti(request, owner_id=None, group_id=None):
    """Renders the canvas page for drawing graffiti."""
    target_user = target_group = None
    if owner_id is not None:
        target_user = get_object_or_404(User, pk=owner_id)
        if not can_view(request.user, target_user, target_user.profile.privacy_wall_post):
            return redirect('profiles:view', user_id=owner_id)
        save_url = '/wall/graffiti/save/user/' + str(owner_id) + '/'
        cancel_url = redirect('profiles:view', user_id=owner_id).url
        title = 'Граффити для ' + target_user.get_full_name()
    else:
        target_group = get_object_or_404(Group, pk=group_id)
        if not target_group.is_member(request.user) and target_group.owner_id != request.user.id:
            return redirect('groups:view', group_id=group_id)
        save_url = '/wall/graffiti/save/group/' + str(group_id) + '/'
        cancel_url = redirect('groups:view', group_id=group_id).url
        title = 'Граффити в группу ' + target_group.name
    template = 'wall/_graffiti_inner.html' if request.headers.get('HX-Request') else 'wall/graffiti.html'
    return render(request, template, {
        'title': title,
        'save_url': save_url,
        'cancel_url': cancel_url,
    })


def _decode_data_url(data_url):
    """Returns (ContentFile, ext) or (None, None) on bad input."""
    if not data_url or not data_url.startswith('data:image/'):
        return None, None
    try:
        header, b64 = data_url.split(',', 1)
        ext = header.split('/', 1)[1].split(';', 1)[0]
        if ext not in ('png', 'jpeg', 'jpg'):
            return None, None
        raw = base64.b64decode(b64, validate=True)
    except (ValueError, binascii.Error):
        return None, None
    if len(raw) > 2 * 1024 * 1024:  # 2 MB cap on a 586x408 PNG is plenty
        return None, None
    return ContentFile(raw), ext


@login_required
@require_POST
def save_graffiti_user(request, owner_id):
    owner = get_object_or_404(User, pk=owner_id)
    if not can_view(request.user, owner, owner.profile.privacy_wall_post):
        return redirect('profiles:view', user_id=owner_id)
    cf, ext = _decode_data_url(request.POST.get('image_data', ''))
    if cf is None:
        messages.error(request, 'Не удалось сохранить граффити.')
        return redirect('wall:graffiti_user', owner_id=owner_id)
    wp = WallPost(owner=owner, author=request.user, text='')
    wp.graffiti.save(f'graffiti_{uuid.uuid4().hex}.{ext}', cf, save=True)
    from messaging.consumers import push_notif_for_wall_post
    from .consumers import push_wall
    push_notif_for_wall_post(wp)
    push_wall(owner=owner)
    return redirect('profiles:view', user_id=owner_id)


@login_required
@require_POST
def save_graffiti_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if not group.is_member(request.user) and group.owner_id != request.user.id:
        return redirect('groups:view', group_id=group_id)
    cf, ext = _decode_data_url(request.POST.get('image_data', ''))
    if cf is None:
        messages.error(request, 'Не удалось сохранить граффити.')
        return redirect('wall:graffiti_group', group_id=group_id)
    wp = WallPost(group=group, author=request.user, text='')
    wp.graffiti.save(f'graffiti_{uuid.uuid4().hex}.{ext}', cf, save=True)
    from messaging.consumers import push_notif_for_wall_post
    from .consumers import push_wall
    push_notif_for_wall_post(wp)
    push_wall(group=group)
    return redirect('groups:view', group_id=group_id)


@login_required
@require_POST
def comment(request, post_id):
    wp = get_object_or_404(WallPost, pk=post_id)
    if wp.owner_id and not can_view(request.user, wp.owner, wp.owner.profile.privacy_wall_view):
        return _redirect_to_target(wp)
    form = WallCommentForm(request.POST)
    if form.is_valid():
        c = form.save(commit=False)
        c.post = wp
        c.author = request.user
        c.save()
        from .consumers import push_wall
        if wp.owner_id:
            push_wall(owner=wp.owner)
        elif wp.group_id:
            push_wall(group=wp.group)
    if request.headers.get('HX-Request'):
        return render(request, 'wall/_post.html', {'p': wp})
    return _redirect_to_target(wp)


def _can_delete_comment(user, c):
    wp = c.post
    return (
        c.author_id == user.id
        or wp.author_id == user.id
        or wp.owner_id == user.id
        or (wp.group_id and wp.group.owner_id == user.id)
    )


@login_required
@require_POST
def delete_comment(request, comment_id):
    from .models import WallComment
    c = get_object_or_404(WallComment, pk=comment_id)
    wp = c.post
    if not _can_delete_comment(request.user, c):
        return _redirect_to_target(wp)
    owner, group = wp.owner, wp.group
    c.delete()
    from .consumers import push_wall
    if owner is not None:
        push_wall(owner=owner)
    elif group is not None:
        push_wall(group=group)
    return _redirect_to_target(wp)
