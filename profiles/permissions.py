"""Privacy checks. `level` is one of 'all' / 'friends' / 'me'."""

from friends.models import Friendship


def can_view(viewer, owner, level):
    """True if `viewer` may see something on `owner`'s page protected by `level`."""
    if not viewer.is_authenticated:
        return level == 'all'
    if viewer.id == owner.id:
        return True
    if level == 'all':
        return True
    if level == 'me':
        return False
    if level == 'friends':
        return Friendship.state_between(viewer, owner) == 'friends'
    return True


def visibility_flags(viewer, owner):
    """Returns a dict of can_* flags for `owner`'s profile from `viewer`'s perspective."""
    p = owner.profile
    return {
        'can_view_profile': can_view(viewer, owner, p.privacy_profile),
        'can_view_wall':    can_view(viewer, owner, p.privacy_wall_view),
        'can_post_wall':    can_view(viewer, owner, p.privacy_wall_post),
        'can_view_photos':  can_view(viewer, owner, p.privacy_photos),
        'can_view_audio':   can_view(viewer, owner, p.privacy_audio),
        'can_view_video':   can_view(viewer, owner, p.privacy_video),
        'can_view_groups':  can_view(viewer, owner, p.privacy_groups),
        'can_message':      can_view(viewer, owner, p.privacy_messages),
    }
