from django.contrib.auth.tokens import PasswordResetTokenGenerator

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView, FormView, TemplateView
from django.contrib.auth.views import LoginView

from .forms import PlayerUserCreationForm, CroupierUserCreationForm, UserUpdatePicForm

from .models import BaseUser, PlayerUser, CroupierUser, RoomPlayer
from rooms.models import Room
from rooms.forms import RoomCreationForm

from django.contrib.auth.decorators import login_required
import os
from urllib.parse import urlparse, parse_qs

account_activation_token = PasswordResetTokenGenerator()


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
        # Utilizza il valore di room_id come necessario
        url = reverse('rooms:room-overview', kwargs={'pk': self.kwargs.get('room_id')})
        print(url)
        return reverse('rooms:room-overview', kwargs={'pk': self.kwargs.get('room_id')})


@login_required
# from FieldBooking.decorators import player_only
def profile(request, pk):
    if request.method == 'GET':
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

                return render(request, 'users/croupier_profile.html',
                              context={'croupier': croupier, 'room': room, 'form': form, 'form_pic': form_pic})

            return render(request, 'users/croupier_profile.html',
                          context={'croupier': croupier, 'form_pic': form_pic})

        elif user and user.first().is_player:
            # Comportamento per l'utente base (player)
            player = PlayerUser.objects.get(user_id=user_request)
            rooms_query = RoomPlayer.objects.filter(player__user_id=user.first().id)
            rooms = []
            for room in rooms_query:
                rooms.append(Room.objects.get(id=room.room.id))
            # TODO stanze associate al profilo
            print(rooms)
            booking_dict = {}
            return render(request, 'users/player_profile.html',
                          context={'player': player, 'form_pic': form_pic, 'rooms': rooms})


def saldo_update(request, pk):
    player = get_object_or_404(PlayerUser, user_id=pk)
    if request.method == 'POST':
        saldo = request.POST.get('saldo')
        saldo = float(saldo)
        player.saldo += float(round(saldo, 2))
        player.saldo = round(player.saldo, 2)
        print(player.saldo)
        player.save()

    return redirect('users:profile', pk)


def pic_update(request, pk):
    user = get_object_or_404(BaseUser, id=pk)
    if request.method == 'POST':
        form = UserUpdatePicForm(request.POST, request.FILES, instance=user)
        # TODO: il form non è valido una volta compilato, perchè?
        if form.is_valid():
            if not user.profile_pic:
                user.profile_pic = "profile_pics/profile_no_pic.png"
                user.save()

            form.save()

    return redirect('users:profile', pk)


def room_player_delete(request, room_pk):
    # TODO non elimina alcuna relazione
    if request.method == "POST":
        # room_player = get_object_or_404(RoomPlayer, room_id=room_pk, player__user_id=request.user.id)
        # room_player = RoomPlayer.objects.get(room_id=room_pk, player__user_id=request.user.id)
        player = get_object_or_404(PlayerUser, user_id=request.user.id)
        room = get_object_or_404(Room, id=room_pk)
        player.rooms.remove(room)
        player.save()
        room.seats_occupied -= 1
        room.save()
        return redirect("users:profile", request.user.id)
