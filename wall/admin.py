from django.contrib import admin

from .models import WallComment, WallPost

admin.site.register(WallPost)
admin.site.register(WallComment)
