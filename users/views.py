from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView
from django.contrib.auth.views import LoginView

from .forms import PlayerUserCreationForm, CroupierUserCreationForm, UserUpdatePicForm

from .models import BaseUser, PlayerUser, CroupierUser, RoomPlayer, Giocata
from rooms.models import Room
from rooms.forms import RoomCreationForm

from django.db.models import Sum

from django.contrib.auth.decorators import login_required


class SignUpView(CreateView):
    form_class = UserCreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("users:homepage")


class PlayerSignUpView(CreateView):
    model = BaseUser
    form_class = PlayerUserCreationForm
    template_name = "registration/signup_form.html"

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'player'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        PlayerUser.objects.create(user=user, saldo=100)
        login(self.request, user)
        return redirect('users:homepage')


class CroupierSignUpView(CreateView):
    model = BaseUser
    form_class = CroupierUserCreationForm
    template_name = "registration/signup_form.html"

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'croupier'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        croupier = CroupierUser.objects.create(user=user)
        login(self.request, user)
        return redirect('users:homepage')


class CustomLoginView(LoginView):

    def get_success_url(self):
        return reverse('rooms:room-overview', kwargs={'pk': self.kwargs.get('room_id')})


@login_required
def profile(request, pk):
    if request.method == 'GET' and request.user.id == pk:
        user_request = pk
        user = BaseUser.objects.filter(id=user_request)
        form_pic = UserUpdatePicForm(instance=user[0])
        if user and user.first().is_superuser:
            return render(request, 'users/profile.html', context={'form_pic': form_pic})
        elif user and user.first().is_croupier:
            # Comportamento specifico per il croupier
            croupier = CroupierUser.objects.get(user_id=user_request)
            if croupier.room:
                room = Room.objects.get(id=croupier.room_id)
                form = RoomCreationForm(instance=room)
                giocate = Giocata.objects.filter(room=room.room_name).aggregate(Sum('importo'))
                totale = giocate['importo__sum']
                if totale is None:
                    totale = 0
                else:
                    totale = round(totale, 2)
                return render(request, 'users/croupier_profile.html',
                              context={'croupier': croupier, 'room': room, 'form': form, 'form_pic': form_pic,
                                       'totale': totale})

            return render(request, 'users/croupier_profile.html',
                          context={'croupier': croupier, 'form_pic': form_pic})

        elif user and user.first().is_player:
            # Comportamento per il player
            player = PlayerUser.objects.get(user_id=user_request)
            rooms_query = RoomPlayer.objects.filter(player__user_id=user.first().id)
            storico = Giocata.objects.filter(player__user_id=user.first().id).order_by("-timestamp")
            rooms = []
            for room in rooms_query:
                rooms.append(Room.objects.get(id=room.room.id))
            return render(request, 'users/player_profile.html',
                          context={'player': player, 'form_pic': form_pic, 'rooms': rooms, 'storico': storico})
    return redirect("users:homepage")


def saldo_update(request, pk):
    player = get_object_or_404(PlayerUser, user_id=pk)
    if request.method == 'POST':
        saldo = request.POST.get('saldo')
        saldo = float(saldo)
        ricarica = round(saldo, 2)
        giocata = Giocata(player=player, importo=ricarica, is_ricarica=True)
        giocata.save()

    return redirect('users:profile', pk)


def saldo_bet(request, user_pk, room_pk):
    player = get_object_or_404(PlayerUser, user_id=user_pk)
    room = get_object_or_404(Room, id=room_pk)
    if request.method == 'POST':
        saldo = request.POST.get('saldo')
        saldo = float(saldo)
        ricarica = round(saldo, 2)
        giocata = Giocata(player=player, importo=ricarica, is_ricarica=False, room=room.room_name)
        giocata.save()

    return redirect('rooms:room-overview', room_pk)


def pic_update(request, pk):
    user = get_object_or_404(BaseUser, id=pk)
    if request.method == 'POST':
        form = UserUpdatePicForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            if not user.profile_pic:
                user.profile_pic = "profile_pics/profile_no_pic.png"
                user.save()

            form.save()

    return redirect('users:profile', pk)


def room_player_delete(request, room_pk):
    if request.method == "POST":
        player = get_object_or_404(PlayerUser, user_id=request.user.id)
        room = get_object_or_404(Room, id=room_pk)
        player.rooms.remove(room)
        player.save()
        room.seats_occupied -= 1
        room.save()
        return redirect("users:profile", request.user.id)
