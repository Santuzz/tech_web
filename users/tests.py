from django.test import TestCase
from django.urls import reverse
from .models import BaseUser, PlayerUser, CroupierUser, RoomPlayer, Giocata
from rooms.models import Room, Section
from django.contrib import auth

from datetime import time


def createPlayer(email, username, pwd, first_name, last_name):
    user = BaseUser.objects.create_user(email=email, username=username, password=pwd)
    user.first_name = first_name
    user.last_name = last_name
    user.is_player = True
    user.save()
    PlayerUser.objects.get_or_create(user=user)
    return user


def createCroupier(email, username, pwd, first_name, last_name):
    user = BaseUser.objects.create_user(email=email, username=username, password=pwd)
    user.first_name = first_name
    user.last_name = last_name
    user.is_croupier = True
    user.save()
    CroupierUser.objects.get_or_create(user=user)
    return user


def createRoom(section, name, seats, bet, opening, closing, occupied, croupier):
    room = Room.objects.create(
        section=section,
        room_name=name,
        seats_number=seats,
        minimum_bet=bet,
        opening=opening,
        closing=closing,
        seats_occupied=occupied
    )
    room.save()
    croupier_room = CroupierUser.objects.get(user=croupier)
    croupier_room.room = room
    croupier_room.save()
    return room


class ProfileViewTest(TestCase):
    def setUp(self):
        self.player = createPlayer('test@example.com', 'testplayer', 'testpassword', 'test', 'player')
        self.player_user = PlayerUser.objects.get(user=self.player)
        self.croupier = createCroupier('test_cr@example.com', 'croupier', 'testpassword', 'test', 'croupier')
        section = Section.objects.create(section_name="Roulette")
        self.room = createRoom(section, "casa", 100, "0.10", time(hour=8, minute=00), time(hour=23, minute=00), 5,
                               self.croupier)
        self.room_player = RoomPlayer.objects.create(room=self.room, player=self.player_user)
        self.giocata = Giocata.objects.create(
            player=PlayerUser.objects.get(user=self.player),
            importo=5,
            room=self.room.room_name
        )

    """
    testiamo il caso in cui un utente provi ad accedere al profilo di un altro utente
    """

    def test_wrong_user_id_redirect(self):
        self.client.force_login(self.player)
        auth_player = auth.get_user(self.client)
        self.assertEqual(auth_player.is_authenticated, True)
        response = self.client.get(reverse('users:profile', args=[29]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('users:homepage'))

    """
    testiamo il caso in cui un player, iscritto ad una sala e in cui abbia giocato una volta, provi ad accedere al suo profilo
    """

    def test_player_login(self):
        self.client.force_login(self.player)
        auth_player = auth.get_user(self.client)
        self.assertEqual(auth_player.is_authenticated, True)
        response = self.client.get(reverse('users:profile', args=[self.player.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.username)
        self.assertContains(response, self.room.room_name)
        self.assertContains(response, self.giocata.importo)

    """
        testiamo il caso in cui un player si disicriva dalla sala per verificare che la sala sia rimossa dalle relazioni ma che rimangano le giocate collegate
        """

    def test_player_login_unsubscribe_to_room(self):
        self.client.force_login(self.player)
        auth_player = auth.get_user(self.client)
        self.assertEqual(auth_player.is_authenticated, True)
        response = self.client.get(reverse('users:profile', args=[self.player.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.username)
        response = self.client.post(reverse('users:delete-room-player', args=[self.room.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(RoomPlayer.objects.filter(player=self.player_user, room=self.room).exists())
        response = self.client.get(reverse('users:profile', args=[self.player.id]))
        self.assertContains(response, self.giocata.importo)

    """
        testiamo il caso in cui un player effettua una ricarica e il saldo viene incrementato
        (test della funzione update_saldo
        """
    def test_player_makes_ricarica(self):
        self.client.force_login(self.player)
        auth_croupier = auth.get_user(self.client)
        self.assertEqual(auth_croupier.is_authenticated, True)
        updated_user = PlayerUser.objects.get(user=self.player)
        self.assertEqual(updated_user.saldo, 5.00)
        response = self.client.post(reverse('users:update_saldo', args=[self.player.id]), {'saldo': 10.00})
        self.assertEqual(response.status_code, 302)
        updated_user = PlayerUser.objects.get(user=self.player)
        giocata=Giocata.objects.get(is_ricarica=True)
        self.assertEqual(updated_user.saldo, 15.00)
        self.assertIsNotNone(giocata)

    """
    testiamo il caso in cui un croupier, possessore di una stanza, provi ad accedere al suo profilo 
    """

    def test_croupier_login(self):
        self.client.force_login(self.croupier)
        auth_croupier = auth.get_user(self.client)
        self.assertEqual(auth_croupier.is_authenticated, True)
        response = self.client.get(reverse('users:profile', args=[self.croupier.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.croupier.username)
        self.assertContains(response, self.room.room_name)
