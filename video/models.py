from django.conf import settings
from django.db import models


class Video(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='videos',
    )
    title = models.CharField('название', max_length=200)
    description = models.TextField('описание', blank=True)
    file = models.FileField(upload_to='videos/%Y/%m/')
    preview = models.ImageField(
        'обложка', upload_to='videos/%Y/%m/previews/', blank=True, null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def preview_url(self):
        if self.preview:
            return self.preview.url
        return '/static/img/no_video.png'


class VideoComment(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='video_comments',
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
