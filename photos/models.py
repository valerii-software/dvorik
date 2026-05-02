import io
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageOps


class Album(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='albums',
    )
    title = models.CharField('название', max_length=120)
    description = models.TextField('описание', blank=True)
    cover = models.ForeignKey(
        'Photo', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='+',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def cover_url(self):
        if self.cover and self.cover.thumbnail:
            return self.cover.thumbnail.url
        first = self.photos.first()
        if first and first.thumbnail:
            return first.thumbnail.url
        return '/static/img/no_album.png'

    @property
    def photo_count(self):
        return self.photos.count()


class Photo(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='photos')
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='uploaded_photos',
    )
    image = models.ImageField(upload_to='photos/%Y/%m/')
    thumbnail = models.ImageField(upload_to='photos/%Y/%m/thumbs/', blank=True, null=True)
    description = models.CharField('описание', max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image and not self.thumbnail:
            self._make_thumbnail()
            super().save(update_fields=['thumbnail'])

    def _make_thumbnail(self):
        with Image.open(self.image.path) as im:
            im = ImageOps.exif_transpose(im)
            im = im.convert('RGB')
            im = ImageOps.fit(im, (200, 200), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, format='JPEG', quality=82)
            name = Path(self.image.name).stem + '_thumb.jpg'
            self.thumbnail.save(name, ContentFile(buf.getvalue()), save=False)

    def neighbours(self):
        ids = list(self.album.photos.values_list('id', flat=True))
        try:
            i = ids.index(self.id)
        except ValueError:
            return None, None
        prev_id = ids[i - 1] if i > 0 else None
        next_id = ids[i + 1] if i < len(ids) - 1 else None
        return prev_id, next_id


class PhotoTag(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='tags')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='photo_tags',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='created_photo_tags',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('photo', 'user')]


class PhotoComment(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='photo_comments',
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
