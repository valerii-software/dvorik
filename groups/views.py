from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from profiles.permissions import can_view
from wall.forms import WallPostForm
from wall.models import WallPost

from .forms import GroupForm, GroupSettingsForm
from .models import Group, GroupLink, GroupMember

User = get_user_model()


@login_required
def all_groups(request):
    q = request.GET.get('q', '').strip()
    qs = Group.objects.all()
    if q:
        qs = qs.filter(Q(name__icontains=q) | Q(description__icontains=q))
    return render(request, 'groups/all.html', {
        'section': 'all_groups',
        'q': q,
        'groups': qs[:60],
    })


@login_required
def my_groups(request):
    return user_groups(request, request.user.id)


@login_required
def user_groups(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    if not can_view(request.user, user, user.profile.privacy_groups):
        return render(request, 'profiles/denied.html', {
            'pageuser': user,
            'message': 'Группы этого пользователя скрыты настройками приватности.',
        }, status=403)
    group_ids = list(GroupMember.objects.filter(user=user).values_list('group_id', flat=True))
    groups = Group.objects.filter(id__in=group_ids)
    return render(request, 'groups/list.html', {
        'section': 'my_groups' if user.id == request.user.id else None,
        'pageuser': user,
        'is_me': user.id == request.user.id,
        'groups': groups,
    })


@login_required
def view(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    posts = WallPost.objects.filter(group=group).select_related('author', 'author__profile')
    members_preview = group.memberships.select_related('user', 'user__profile')[:6]
    linked_groups = [gl.linked for gl in group.outgoing_links.select_related('linked')]
    return render(request, 'groups/view.html', {
        'group': group,
        'is_member': group.is_member(request.user),
        'is_owner': group.owner_id == request.user.id,
        'posts': posts,
        'members_preview': members_preview,
        'linked_groups': linked_groups,
        'wall_form': WallPostForm(),
    })


@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST, request.FILES)
        if form.is_valid():
            group = form.save(commit=False)
            group.owner = request.user
            group.save()
            GroupMember.objects.create(group=group, user=request.user)
            return redirect('groups:view', group_id=group.id)
    else:
        form = GroupForm()
    return render(request, 'groups/form.html', {
        'section': 'my_groups',
        'form': form,
        'mode': 'create',
    })


@login_required
def edit_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id, owner=request.user)
    if request.method == 'POST':
        form = GroupSettingsForm(
            request.POST, request.FILES, instance=group, owner=request.user,
        )
        if form.is_valid():
            instance = form.save()
            form.save_links(instance)
            return redirect('groups:view', group_id=group.id)
    else:
        form = GroupSettingsForm(instance=group, owner=request.user)
    return render(request, 'groups/form.html', {
        'form': form,
        'group': group,
        'mode': 'edit',
    })


@login_required
@require_POST
def delete_group(request, group_id):
    group = get_object_or_404(Group, pk=group_id, owner=request.user)
    group.delete()
    messages.info(request, 'Группа удалена.')
    return redirect('groups:my_groups')


@login_required
@require_POST
def join(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    GroupMember.objects.get_or_create(group=group, user=request.user)
    return redirect('groups:view', group_id=group.id)


@login_required
@require_POST
def leave(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    if group.owner_id == request.user.id:
        messages.error(request, 'Владелец не может покинуть группу.')
    else:
        GroupMember.objects.filter(group=group, user=request.user).delete()
    return redirect('groups:view', group_id=group.id)


@login_required
def members(request, group_id):
    group = get_object_or_404(Group, pk=group_id)
    members = group.memberships.select_related('user', 'user__profile')
    return render(request, 'groups/members.html', {
        'group': group,
        'members': members,
    })
