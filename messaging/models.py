from django.conf import settings
from django.db import models
from django.db.models import Count
from django.urls import reverse


class Dialog(models.Model):
    """A chat: 1-to-1 (no name, two human participants), a multi-user
    group chat (has a name), or a user-to-group conversation (target_group
    is set, participants are the user + the group's owner; messages from
    the owner render with the group's identity)."""

    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='chats',
    )
    name = models.CharField('название', max_length=120, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_chats',
    )
    target_group = models.ForeignKey(
        'groups.Group',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='dialogs',
    )
    last_message_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-last_message_at', '-id']

    def __str__(self):
        return self.name or f'dialog<{self.id}>'

    @property
    def is_group(self):
        return bool(self.name)

    @property
    def is_user_to_group(self):
        return self.target_group_id is not None

    def other(self, user):
        """For 1-on-1, returns the other participant. For groups returns None."""
        if self.is_group:
            return None
        return self.participants.exclude(id=user.id).first()

    def title_for(self, viewer):
        if self.is_user_to_group:
            tg = self.target_group
            if viewer.id == tg.owner_id:
                # Admin sees the user's name (their interlocutor)
                other = self.participants.exclude(id=viewer.id).first()
                return other.get_full_name() if other else tg.name
            return tg.name
        if self.is_group:
            return self.name
        o = self.other(viewer)
        return o.get_full_name() if o else 'Чат'

    def avatar_for(self, viewer):
        if self.is_user_to_group:
            tg = self.target_group
            if viewer.id == tg.owner_id:
                other = self.participants.exclude(id=viewer.id).first()
                return other.profile.avatar_url if other else tg.avatar_url
            return tg.avatar_url
        if self.is_group:
            return '/static/img/no_group.png'
        o = self.other(viewer)
        return o.profile.avatar_url if o else '/static/img/no_photo.png'

    @classmethod
    def get_or_create_one_to_one(cls, u1, u2):
        """Find an existing 1-on-1 between u1 and u2 (no name, exactly two
        participants, no target_group), or create one."""
        existing = (
            cls.objects
            .filter(name='', target_group__isnull=True, participants=u1)
            .filter(participants=u2)
            .annotate(c=Count('participants'))
            .filter(c=2)
            .first()
        )
        if existing:
            return existing
        d = cls.objects.create()
        d.participants.add(u1, u2)
        return d

    @classmethod
    def get_or_create_user_to_group(cls, user, group):
        """User-to-group dialog. Owner = group.owner; participants = user + owner."""
        existing = cls.objects.filter(target_group=group, participants=user).first()
        if existing:
            return existing
        d = cls.objects.create(target_group=group)
        d.participants.add(user, group.owner)
        return d

    @classmethod
    def for_user(cls, user):
        return (
            cls.objects.filter(participants=user)
            .distinct()
            .prefetch_related('participants', 'participants__profile')
        )


class Message(models.Model):
    dialog = models.ForeignKey(Dialog, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages',
    )
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to='messages/%Y/%m/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)  # legacy 1-on-1 read marker

    class Meta:
        ordering = ['created_at']

    def _as_group(self):
        """In a user-to-group dialog, the owner's messages render as the
        group itself (avatar, name, link to /groups/<id>/)."""
        d = self.dialog
        if d.target_group_id and self.sender_id == d.target_group.owner_id:
            return d.target_group
        return None

    @property
    def display_avatar(self):
        g = self._as_group()
        return g.avatar_url if g else self.sender.profile.avatar_url

    @property
    def display_name(self):
        g = self._as_group()
        return g.name if g else self.sender.get_full_name()

    @property
    def display_url(self):
        g = self._as_group()
        if g:
            return reverse('groups:view', args=[g.id])
        return reverse('profiles:view', args=[self.sender_id])
