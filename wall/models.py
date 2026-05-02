from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse


class WallPost(models.Model):
    """A post on a user's wall OR a group's wall.

    Exactly one of (owner, group) must be set.
    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='wall_posts_received',
        null=True, blank=True,
    )
    group = models.ForeignKey(
        'groups.Group', on_delete=models.CASCADE,
        related_name='posts',
        null=True, blank=True,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='wall_posts_authored',
    )
    text = models.TextField(blank=True)
    graffiti = models.ImageField(upload_to='graffiti/%Y/%m/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(owner__isnull=False, group__isnull=True) |
                    models.Q(owner__isnull=True, group__isnull=False)
                ),
                name='wallpost_owner_xor_group',
            ),
        ]

    def __str__(self):
        target = f'user {self.owner_id}' if self.owner_id else f'group {self.group_id}'
        return f'wallpost #{self.pk} on {target} by {self.author_id}'

    def clean(self):
        if bool(self.owner_id) == bool(self.group_id):
            raise ValidationError('Set either owner or group, not both.')

    @property
    def is_group_post(self):
        return self.group_id is not None

    @property
    def target_url(self):
        if self.group_id:
            return reverse('groups:view', args=[self.group_id])
        return reverse('profiles:view', args=[self.owner_id])

    @property
    def target_name(self):
        if self.group_id:
            return self.group.name
        return self.owner.get_full_name()


class WallComment(models.Model):
    post = models.ForeignKey(WallPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='wall_comments',
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
