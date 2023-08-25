from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView

from datetime import datetime
import pytz

from .models import Room, Section
from .forms import RoomCreationForm
from users.models import CroupierUser, BaseUser, PlayerUser, RoomPlayer
from django.db.models import F


class CreateRoom(CreateView):
    model = Room
    form_class = RoomCreationForm
    template_name = "registration/create_room.html"
    success_url = reverse_lazy("rooms:homepage")
    croupier = None

    def dispatch(self, request, *args, **kwargs):
        self.croupier = CroupierUser.objects.filter(user_id=kwargs['user_id'])[:1].get()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.croupier.room:
            context['room'] = False
        else:
            context['room'] = True
        return context

    def form_valid(self, form):
        if self.request.method == "POST":
            form = RoomCreationForm(self.request.POST, self.request.FILES)
            room = form.save()
            self.croupier.room = room
            self.croupier.save()

        return super().form_valid(form)


def room_update(request, room_pk, croupier_pk):
    room = get_object_or_404(Room, id=room_pk)
    if request.method == 'POST':
        form = RoomCreationForm(request.POST, request.FILES, instance=room)
        print(request.FILES)
        if form.is_valid():
            if not room.cover_pic:
                room.cover_pic = "room_thumbnail/room_no_thumb.png"
                room.save()

            form.save()

    return redirect('users:profile', croupier_pk)


def room_delete(request, room_pk, croupier_pk):
    room = Room.objects.filter(id=room_pk)
    croupier = get_object_or_404(CroupierUser, user_id=croupier_pk)
    croupier.room = None
    croupier.save()
    room.delete()
    return redirect('users:profile', croupier_pk)


def room_signup(request, room_id):
    room = Room.objects.get(id=room_id)
    user_player = BaseUser.objects.get(username=request.user.username)
    player = PlayerUser.objects.get(user_id=user_player.id)
    room_player = RoomPlayer.objects.create(room=room, player=player)  # Crea un nuovo oggetto RoomPlayer
    room_player.save()
    return redirect('rooms:room-overview', room_id)


def room_overview(request, pk):
    current_time = []
    if request.method == 'GET':
        room_request = pk
        room = Room.objects.get(id=room_request)
        croupier = CroupierUser.objects.get(room_id=room.id)
        user = BaseUser.objects.get(id=croupier.user_id)
        print(request.user)
        user_player = BaseUser.objects.get(id=request.user.id)
        utc_now = datetime.now(pytz.utc)
        italy_tz = pytz.timezone('Europe/Rome')
        now = utc_now.astimezone(italy_tz)

        current_time.append(now.strftime("%H"))
        current_time.append(now.strftime("%M"))
        if request.user.is_player:
            player = PlayerUser.objects.get(user_id=user_player.id)
            has_room = player.rooms.filter(pk=room.id).exists()
            return render(request, 'rooms/detail_room.html', context={'room': room,
                                                                      'croupier': user,
                                                                      'has_room': has_room,
                                                                      'player': player,
                                                                      'time': current_time})
        return render(request, 'rooms/detail_room.html', context={'room': room,
                                                                  'croupier': user,
                                                                  'has_room': False,
                                                                  'time': current_time})


def search_room(request):
    if request.method == 'GET':
        section_type = request.GET.get('section-type')
        seats_number = request.GET.get('seats-number')
        minimum_bet = request.GET.get('minimum-bet')
        opening = request.GET.get('opening-time')
        opening_time = None
        if opening != "" and opening is not None:
            opening_time = datetime.strptime(opening, '%H:%M').time()
        closing = request.GET.get('closing-time')
        closing_time = None
        if closing != "" and closing is not None:
            closing_time = datetime.strptime(closing, '%H:%M').time()
        seats_available = request.GET.get('seats-available')
        rooms = Room.objects.filter(section__section_name=section_type).order_by('room_name')
        if seats_number is not None and seats_number != "":
            rooms = rooms.filter(seats_number__lt=int(seats_number))
        if minimum_bet is not None and minimum_bet != "":
            rooms = rooms.filter(minimum_bet=minimum_bet)
        if opening_time is not None:
            rooms = rooms.filter(opening__lte=opening_time)
        if closing_time is not None:
            rooms = rooms.filter(closing__gte=closing_time)
        if seats_available is not None and seats_available == 'on':
            rooms = rooms.filter(seats_occupied__lt=F('seats_number'))

        section_dict = Section.objects.values('id', 'section_name')
        section = [elemento['section_name'] for index, elemento in enumerate(section_dict)]
        room_dict = {}
        for index, room_object in enumerate(rooms):
            room_tmp = Room.objects.filter(section__section_name=section_type, id=room_object.id).values()

            if len(room_tmp) > 0:
                room_dict[index] = room_tmp

        if request.user.is_authenticated and request.user.is_player:
            user = BaseUser.objects.get(username=request.user.username)
            player = PlayerUser.objects.get(user_id=user.id)

            return render(request, 'rooms/search_room.html', context={'room': room_dict,
                                                                      'section': section,
                                                                      'player': player})

        return render(request, 'rooms/search_room.html', context={'room': room_dict,
                                                                  'section': section,
                                                                  })
