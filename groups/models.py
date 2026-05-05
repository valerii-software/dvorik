from django.conf import settings
from django.db import models


class Group(models.Model):
    name = models.CharField('название', max_length=120)
    description = models.TextField('описание', blank=True)
    avatar = models.ImageField(upload_to='groups/', blank=True, null=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='owned_groups',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return '/static/img/no_group.png'

    @property
    def members_count(self):
        return self.memberships.count()

    def is_member(self, user):
        if not user.is_authenticated:
            return False
        return self.memberships.filter(user=user).exists()


class GroupMember(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='group_memberships',
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('group', 'user')]
        ordering = ['joined_at']


class GroupLink(models.Model):
    """Recommendations the admin pins on the group's right sidebar.
    Both ends are groups; the linked side is whatever group the admin
    is themselves a member of."""
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name='outgoing_links',
    )
    linked = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name='incoming_links',
    )
    position = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('group', 'linked')]
        ordering = ['position', 'id']
