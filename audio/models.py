from django.conf import settings
from django.db import models


class AudioTrack(models.Model):
    artist = models.CharField('исполнитель', max_length=120)
    title = models.CharField('название', max_length=200)
    file = models.FileField(upload_to='audio/%Y/%m/')
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='uploaded_tracks',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.artist} — {self.title}'


class UserAudio(models.Model):
    """A track in a user's personal collection."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='audio_collection',
    )
    track = models.ForeignKey(AudioTrack, on_delete=models.CASCADE, related_name='in_collections')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('user', 'track')]
        ordering = ['-added_at']
