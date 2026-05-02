from django.conf import settings
from django.db import models
from django.db.models import Q


class Dialog(models.Model):
    """A 1-to-1 conversation. user_a.id < user_b.id always."""
    user_a = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dialogs_a',
    )
    user_b = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dialogs_b',
    )
    last_message_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [('user_a', 'user_b')]
        ordering = ['-last_message_at']

    @classmethod
    def get_or_create_between(cls, u1, u2):
        a, b = sorted([u1, u2], key=lambda u: u.id)
        dialog, _ = cls.objects.get_or_create(user_a=a, user_b=b)
        return dialog

    def other(self, user):
        return self.user_b if self.user_a_id == user.id else self.user_a

    @classmethod
    def for_user(cls, user):
        return cls.objects.filter(Q(user_a=user) | Q(user_b=user)).select_related(
            'user_a', 'user_a__profile', 'user_b', 'user_b__profile'
        )


class Message(models.Model):
    dialog = models.ForeignKey(Dialog, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages',
    )
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to='messages/%Y/%m/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_at']
