from django.contrib import admin

from .models import AudioTrack, UserAudio

admin.site.register(AudioTrack)
admin.site.register(UserAudio)
