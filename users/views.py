from django.contrib.auth.tokens import PasswordResetTokenGenerator

from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView, FormView, TemplateView
from .forms import UserUpdateProfilePic, PlayerUserCreationForm, CroupierUserCreationForm

from .models import BaseUser, PlayerUser, CroupierUser
from rooms.models import Room
from rooms.forms import RoomCreationForm

from django.contrib.auth.decorators import login_required
import os

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


@login_required
# from FieldBooking.decorators import player_only
def Profile(request, pk):
    if request.method == 'GET':
        user_request = pk
        user = BaseUser.objects.filter(id=user_request)

        if user and user.first().is_superuser:
            return render(request, 'users/profile.html', context={})
        elif user and user.first().is_croupier:
            # Comportamento specifico per il croupier
            croupier = CroupierUser.objects.get(user_id=user_request)
            if croupier.room:
                room = Room.objects.get(id=croupier.room_id)
                form = RoomCreationForm(instance=room)
                return render(request, 'users/croupier_profile.html',
                              context={'croupier': croupier, 'room': room, 'form': form})
            return render(request, 'users/croupier_profile.html',
                          context={'croupier': croupier})
        elif user and user.first().is_player:
            # Comportamento per l'utente base (player)

            player = PlayerUser.objects.get(user_id=user_request)
            # TODO stanze associate al profilo
            booking_dict = {}
            return render(request, 'users/player_profile.html', context={'player': player})


def SaldoUpdate(request, pk):
    player = get_object_or_404(PlayerUser, user_id=pk)

    if request.method == 'POST':
        saldo = request.POST.get('saldo')
        if saldo != '':
            if float(saldo) > 0:
                player.saldo += float(saldo)
                player.save()

    return redirect('users:profile', pk)


class UpdateProfilePic(UpdateView):
    model = BaseUser
    template_name = "users/update_profile_pic.html"
    form_class = UserUpdateProfilePic

