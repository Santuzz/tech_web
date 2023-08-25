from django.contrib import auth
from django.urls import reverse
from datetime import time
from django.test import TestCase
from users.models import BaseUser, PlayerUser
import json


def createUser(email, username, password, first_name, last_name):
    user = BaseUser.objects.create_user(email=email, username=username, password=password, first_name=first_name,
                                        last_name=last_name)
    user.save()
    return user


def createPlayer(email, username, password, first_name, last_name):
    user = createUser(email, username, password, first_name, last_name)
    player = PlayerUser.objects.create(use)


def createClub(user, club_name, street, civic_number, city, zipcode, ):
    club = Club.objects.create(club_name=club_name, street=street, civic_number=civic_number,
                               city=city, zip_code=zipcode, user=user)
    user.set_has_club()

    return club


def createPadelField(club, fn):
    field_number = fn
    hourly_cost = 12.50
    first_booking = time(hour=8, minute=00)
    last_booking = time(hour=23, minute=00)
    pf = PadelField.objects.create(club=club, field_number=field_number, hourly_cost=hourly_cost,
                                   first_booking=first_booking, last_booking=last_booking)
    return pf


'''
Test che controlla che la get_queryset di PadelField ritorni solo i campi dell'utente che manda la richiesta 
'''


class PadelViewListTests(TestCase):

    def setUp(self):
        print("-------------  " + type(self).__name__ + "  -------------")

        self.acc = createAccount(True, 'emaildiprova@prova.com', 'username', 'test', 'test', 'pwd')
        self.club = createClub(self.acc, 'test_club', 'via di prova', '57456', 'prova', '457')

        self.acc2 = createAccount(True, 'p@p.com', 'test2', 't', 't', 'pwd')
        self.club2 = createClub(self.acc2, 'club2', 'via di prova', '458', 'prova', '12')

        self.player = createAccount(False, 't@t.com', 'player', 't', 't', 'pwd')

    def test_padellist_view_with_user_different(self):
        createPadelField(self.club, 1)
        self.client.force_login(self.acc2)
        user = auth.get_user(self.client)
        self.assertEqual(user.is_authenticated, True)
        response = self.client.get(reverse('club_background:padel-list'))
        for padel in response.context['object_list']:
            self.assertNotEqual(padel.club.user.id, self.acc1.id)

    def test_padellist_view_with_user_ok(self):

        createPadelField(self.club, 1)
        self.client.force_login(self.acc)
        user = auth.get_user(self.client)
        self.assertEqual(user.is_authenticated, True)
        response = self.client.get(reverse('club_background:padel-list'))
        for padel in response.context['object_list']:
            self.assertEqual(padel.club.user, user)

    def test_padellist_view_user_not_logged_in(self):
        response = self.client.get(reverse('club_background:padel-list'))
        self.assertEqual(response.status_code, 302)

    def test_padellist_view_user_not_club(self):
        createPadelField(self.club, 1)
        self.client.force_login(self.player)
        user = auth.get_user(self.client)
        self.assertEqual(user.is_authenticated, True)
        response = self.client.get(reverse('club_background:padel-list'))
        self.assertEqual(response.status_code, 302)


'''
Test view che aggiunge un commento(Chiamata ajax)
'''


class AddCommentAJAXviewTests(TestCase):

    def setUp(self):
        print("-------------  " + type(self).__name__ + "  -------------")
        self.acc = createAccount(True, 'emaildiprova@prova.com', 'username', 'test', 'test', 'pwd')
        self.player = createAccount(False, 't@t.com', 'player', 't', 't', 'pwd')
        self.club = createClub(self.acc, 'test_club', 'via di prova', '57456', 'prova', '457')

    def test_add_comment_user_not_logged_in(self):
        data_for_json = {
            "URL": 'http://127.0.0.1:8000/club_background/account/club/1/club-detail',
            "comment": "commento di prova"
        }
        response = self.client.post(reverse('club_background:ajax-add-comment'), data_for_json,
                                    **{'HTTP_X_REQUESTED_WITH':
                                           'XMLHttpRequest'})
        self.assertEqual(response.status_code, 302)

    def test_add_comment_user_logged_in_empty_comment(self):
        data_for_json = {
            "URL": 'http://127.0.0.1:8000/club_background/account/club/1/club-detail',
            "comment": ""
        }
        self.client.force_login(self.player)
        user = auth.get_user(self.client)
        self.assertEqual(user.is_authenticated, True)
        response = self.client.post(reverse('club_background:ajax-add-comment'), data_for_json,
                                    **{'HTTP_X_REQUESTED_WITH':
                                           'XMLHttpRequest'})
        self.assertEqual(response.status_code, 500)

    def test_add_comment_user_logged_in_comment_ok(self):
        data_for_json = {
            "URL": 'http://127.0.0.1:8000/club_background/account/club/1/club-detail',
            "comment": "commento di prova"
        }
        self.client.force_login(self.player)
        user = auth.get_user(self.client)
        self.assertEqual(user.is_authenticated, True)
        response = self.client.post(reverse('club_background:ajax-add-comment'), data_for_json,
                                    **{'HTTP_X_REQUESTED_WITH':
                                           'XMLHttpRequest'})
        self.assertEqual(response.status_code, 200)

    def test_add_comment_user_logged_in_comment_ok_club_not_exist(self):
        data_for_json = {
            "URL": 'http://127.0.0.1:8000/club_background/account/club/2/club-detail',
            "comment": "commento di prova"
        }
        self.client.force_login(self.player)
        user = auth.get_user(self.client)
        self.assertEqual(user.is_authenticated, True)
        response = self.client.post(reverse('club_background:ajax-add-comment'), data_for_json,
                                    **{'HTTP_X_REQUESTED_WITH':
                                           'XMLHttpRequest'})
        self.assertEqual(response.status_code, 500)

    def test_add_comment_user_logged_in_comment_ok_not_ajax_request(self):
        data_for_json = {
            "URL": 'http://127.0.0.1:8000/club_background/account/club/2/club-detail',
            "comment": "commento di prova"
        }
        self.client.force_login(self.player)
        user = auth.get_user(self.client)
        self.assertEqual(user.is_authenticated, True)
        response = self.client.post(reverse('club_background:ajax-add-comment'), data_for_json)
        self.assertEqual(response.status_code, 500)

    def test_add_comment_user_logged_in_comment_ok_GET(self):
        data_for_json = {
            "URL": 'http://127.0.0.1:8000/club_background/account/club/2/club-detail',
            "comment": "commento di prova"
        }
        self.client.force_login(self.player)
        user = auth.get_user(self.client)
        self.assertEqual(user.is_authenticated, True)
        response = self.client.get(reverse('club_background:ajax-add-comment'), data_for_json)
        self.assertEqual(response.status_code, 500)

    def test_add_comment_user_logged_empty_json_data(self):
        data_for_json = {}
        self.client.force_login(self.player)
        user = auth.get_user(self.client)
        self.assertEqual(user.is_authenticated, True)
        response = self.client.post(reverse('club_background:ajax-add-comment'), data_for_json,
                                    **{'HTTP_X_REQUESTED_WITH':
                                           'XMLHttpRequest'})
        self.assertEqual(response.status_code, 500)

    def test_add_comment_user_logged_empty_URL(self):
        data_for_json = {"comment": "commento di prova"}
        self.client.force_login(self.player)
        user = auth.get_user(self.client)
        self.assertEqual(user.is_authenticated, True)
        response = self.client.post(reverse('club_background:ajax-add-comment'), data_for_json,
                                    **{'HTTP_X_REQUESTED_WITH':
                                           'XMLHttpRequest'})
        self.assertEqual(response.status_code, 500)
