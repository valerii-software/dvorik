from django.conf import settings
from django.db import models
from django.db.models import Q


class Friendship(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    STATUS = [(PENDING, 'pending'), (ACCEPTED, 'accepted')]

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='friendships_sent',
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='friendships_received',
    )
    status = models.CharField(max_length=10, choices=STATUS, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [('from_user', 'to_user')]

    @classmethod
    def state_between(cls, me, other):
        """Returns 'friends' | 'sent' | 'received' | 'none'."""
        if me.id == other.id:
            return 'self'
        f = cls.objects.filter(
            (Q(from_user=me, to_user=other) | Q(from_user=other, to_user=me))
        ).first()
        if not f:
            return 'none'
        if f.status == cls.ACCEPTED:
            return 'friends'
        if f.from_user_id == me.id:
            return 'sent'
        return 'received'

    @classmethod
    def friends_qs(cls, user):
        """Returns a queryset of User objects who are accepted friends of `user`."""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        sent = cls.objects.filter(from_user=user, status=cls.ACCEPTED).values_list('to_user_id', flat=True)
        recv = cls.objects.filter(to_user=user, status=cls.ACCEPTED).values_list('from_user_id', flat=True)
        return User.objects.filter(id__in=list(sent) + list(recv)).select_related('profile')

    @classmethod
    def incoming_requests(cls, user):
        return cls.objects.filter(to_user=user, status=cls.PENDING).select_related('from_user', 'from_user__profile')

    @classmethod
    def outgoing_requests(cls, user):
        return cls.objects.filter(from_user=user, status=cls.PENDING).select_related('to_user', 'to_user__profile')
