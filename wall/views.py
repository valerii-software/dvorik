from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import WallCommentForm, WallPostForm
from .models import WallPost

User = get_user_model()


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
def delete_post(request, post_id):
    wp = get_object_or_404(WallPost, pk=post_id)
    if wp.author_id != request.user.id and wp.owner_id != request.user.id:
        return redirect('profiles:view', user_id=wp.owner_id)
    owner_id = wp.owner_id
    wp.delete()
    return redirect('profiles:view', user_id=owner_id)


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
        return render(request, 'wall/_post.html', {'p': wp, 'owner': wp.owner})
    return redirect('profiles:view', user_id=wp.owner_id)
