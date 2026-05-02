from django.conf import settings
from django.db import models
from django.db.models import Count


class Dialog(models.Model):
    """A chat — either 1-to-1 (no name, exactly two participants) or a group
    (has a name, two or more participants)."""

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
    last_message_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-last_message_at', '-id']

    def __str__(self):
        return self.name or f'dialog<{self.id}>'

    @property
    def is_group(self):
        return bool(self.name)

    def other(self, user):
        """For 1-on-1, returns the other participant. For groups returns None."""
        if self.is_group:
            return None
        return self.participants.exclude(id=user.id).first()

    def title_for(self, viewer):
        if self.is_group:
            return self.name
        o = self.other(viewer)
        return o.get_full_name() if o else 'Чат'

    def avatar_for(self, viewer):
        if self.is_group:
            return '/static/img/no_group.png'
        o = self.other(viewer)
        return o.profile.avatar_url if o else '/static/img/no_photo.png'

    @classmethod
    def get_or_create_one_to_one(cls, u1, u2):
        """Find an existing 1-on-1 between u1 and u2 (no name, exactly two
        participants), or create one."""
        existing = (
            cls.objects
            .filter(name='', participants=u1)
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
