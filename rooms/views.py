from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView

from .models import Room, Section
from .forms import RoomCreationForm
from users.models import CroupierUser, BaseUser, PlayerUser, RoomPlayer


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
        print(context['room'])
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
        if form.is_valid():
            if not room.cover_pic:
                room.cover_pic = "room_thumbnail/room_no_thumb.png"
                room.save()

            form.save()

    return redirect('users:profile', croupier_pk)


def room_delete(request, room_pk, croupier_pk):
    room = get_object_or_404(Room, id=room_pk)
    croupier = get_object_or_404(CroupierUser, user_id=croupier_pk)
    croupier.room = None
    croupier.save()
    room.delete()
    room.save()
    return redirect('users:profile', croupier_pk)


def room_signup(request, room_id):
    room = Room.objects.get(id=room_id)
    user_player = BaseUser.objects.get(username=request.user)
    player = PlayerUser.objects.get(user_id=user_player.id)

    room_player = RoomPlayer(room=room, player=player)  # Crea un nuovo oggetto RoomPlayer
    print(room_player)
    room_player.save()
    return redirect('rooms:room-overview')


def room_overview(request, pk):
    if request.method == 'GET':
        room_request = pk
        room = Room.objects.get(id=room_request)
        croupier = CroupierUser.objects.get(room_id=room.id)
        user = BaseUser.objects.get(id=croupier.user_id)
        user_player = BaseUser.objects.get(username=request.user)
        player = PlayerUser.objects.get(user_id=user_player.id)
        has_room = player.rooms.filter(pk=room.id).exists()
        return render(request, 'rooms/detail_room.html', context={'room': room,
                                                                  'croupier': user,
                                                                  'user_room': has_room,
                                                                  'player': player})


def search_room(request):
    if request.method == 'GET':
        section_type = request.GET.get('section-type')
        room = Room.objects.filter(section__section_name=section_type).order_by('room_name')
        section_dict = Section.objects.values('id', 'section_name')
        section = [elemento['section_name'] for index, elemento in enumerate(section_dict)]
        room_dict = {}
        for index, room_object in enumerate(room):
            room_tmp = Room.objects.filter(section__section_name=section_type, id=room_object.id).values()

            if len(room_tmp) > 0:
                room_dict[index] = room_tmp

        if request.user.is_authenticated:
            user = BaseUser.objects.get(username=request.user)
            player = PlayerUser.objects.get(user_id=user.id)

            return render(request, 'rooms/search_room.html', context={'room': room_dict,
                                                              'section': section,
                                                              'player': player})

        return render(request, 'rooms/search_room.html', context={'room': room_dict,
                                                                  'section': section,
                                                                  })
