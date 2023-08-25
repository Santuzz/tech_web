from django.contrib import admin
from .models import CroupierUser, PlayerUser, BaseUser, RoomPlayer, Giocata
from rooms.models import Room, Section

admin.site.register(BaseUser)
admin.site.register(CroupierUser)
admin.site.register(PlayerUser)
admin.site.register(Giocata)
admin.site.register(Room)
admin.site.register(RoomPlayer)
admin.site.register(Section)
