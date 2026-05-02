from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from groups.models import Group

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
    form = WallPostForm(request.POST)
    if form.is_valid():
        wp = form.save(commit=False)
        wp.owner = owner
        wp.author = request.user
        wp.save()
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
    form = WallPostForm(request.POST)
    if form.is_valid():
        wp = form.save(commit=False)
        wp.group = group
        wp.author = request.user
        wp.save()
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
    wp.delete()
    return response


@login_required
@require_POST
def comment(request, post_id):
    wp = get_object_or_404(WallPost, pk=post_id)
    form = WallCommentForm(request.POST)
    if form.is_valid():
        c = form.save(commit=False)
        c.post = wp
        c.author = request.user
        c.save()
    if request.headers.get('HX-Request'):
        return render(request, 'wall/_post.html', {'p': wp})
    return _redirect_to_target(wp)
