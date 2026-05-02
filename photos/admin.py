from django.contrib import admin

from .models import Album, Photo, PhotoComment, PhotoTag

admin.site.register(Album)
admin.site.register(Photo)
admin.site.register(PhotoTag)
admin.site.register(PhotoComment)
