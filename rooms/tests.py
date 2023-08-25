from django.test import TestCase, Client
from django.urls import reverse
from users.models import BaseUser, PlayerUser, CroupierUser, RoomPlayer, Giocata
from .models import Room, Section
from django.contrib import auth
from users.tests import createPlayer, createRoom, createCroupier

from datetime import time


class RoomPlayTest(TestCase):
    def setUp(self):
        self.player = createPlayer('testo@example.com', 'testplayer', 'testpassword', 'test', 'player')
        player = PlayerUser.objects.get(user=self.player)
        self.croupier = createCroupier('test_cr@example.com', 'croupier', 'testpassword', 'test', 'croupier')
        section = Section.objects.create(section_name="Roulette")
        self.room = createRoom(section, "casac", 100, "0.10", time(hour=8, minute=00), time(hour=23, minute=00), 5,
                               self.croupier)
        self.room_player = RoomPlayer.objects.create(room=self.room, player=player)
        self.giocata = Giocata.objects.create(
            player=PlayerUser.objects.get(user=self.player),
            importo=5,
            room=self.room.room_name
        )

    """
    verifichiamo che il player sia iscritto alla sala per poter giocare
    """

    def test_player_is_subscribed(self):
        self.client.force_login(self.player)
        auth_croupier = auth.get_user(self.client)
        self.assertEqual(auth_croupier.is_authenticated, True)
        response = self.client.get(reverse('rooms:room-overview', args=[self.room.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.player.username)

    """
    testiamo un player che effettua una giocata vincente e il saldo viene incrementato
    """

    def test_player_makes_giocata_win(self):
        self.client.force_login(self.player)
        auth_croupier = auth.get_user(self.client)
        self.assertEqual(auth_croupier.is_authenticated, True)
        updated_user = PlayerUser.objects.get(user=self.player)
        self.assertEqual(updated_user.saldo, 5.00)
        response = self.client.post(reverse('users:bet_saldo', args=[self.player.id, self.room.id]), {'saldo': 20.00})
        self.assertEqual(response.status_code, 302)
        updated_user = PlayerUser.objects.get(user=self.player)
        self.assertEqual(updated_user.saldo, 25.00)

    """
    testiamo un player che effettua una giocata perdente e il saldo viene diminuito 
    (test della funzione saldo_bet)
    """

    def test_player_makes_giocata_lose(self):
        self.client.force_login(self.player)
        auth_croupier = auth.get_user(self.client)
        self.assertEqual(auth_croupier.is_authenticated, True)
        updated_user = PlayerUser.objects.get(user=self.player)
        self.assertEqual(updated_user.saldo, 5.00)
        response = self.client.post(reverse('users:bet_saldo', args=[self.player.id, self.room.id]), {'saldo': -5.00})
        self.assertEqual(response.status_code, 302)
        updated_user = PlayerUser.objects.get(user=self.player)
        self.assertEqual(updated_user.saldo, 0.00)
