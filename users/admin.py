from django.contrib import admin
from .models import CroupierUser, PlayerUser, BaseUser, RoomPlayer
from rooms.models import Room

admin.site.register(BaseUser)
admin.site.register(CroupierUser)
admin.site.register(PlayerUser)
admin.site.register(Room)
admin.site.register(RoomPlayer)
