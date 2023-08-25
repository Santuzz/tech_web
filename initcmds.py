from rooms.models import Section
from users.models import *
import os
import random
from django.db import models
from datetime import time


def get_valid_upload_paths(count):
    folder_name = f'media/icon_{count}'
    folder_path = os.path.join(os.getcwd(), folder_name)
    file_extension = '.jpg'

    existing_images = set()
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(file_extension):
                existing_images.add(file)

    valid_paths = []
    for i in range(30):
        found_valid_path = False
        while not found_valid_path:
            file_number = random.randint(0, 10000)
            file_name = f'immagine_{file_number}_{count}{file_extension}'
            file_path = os.path.join(folder_path, file_name)

            if file_name not in existing_images:
                valid_paths.append(f'{folder_name}/{file_name}')
                existing_images.add(file_name)
                found_valid_path = True

    return valid_paths


def erase_db():
    print("cancello il DB")
    Section.objects.all().delete()
    BaseUser.objects.all().delete()


def init_db():
    section = [
        "Roulette",
        "Memory",
        "Slot",
    ]
    if len(Section.objects.all()) != 0:
        return
    sections = []
    for sec in section:
        sections.append(Section.objects.create(section_name=sec))

    if len(BaseUser.objects.all()) != 0:
        return

    # creazione admin
    user = BaseUser.objects.create_user(email="admin@g.com", username="admin", password="admin", first_name="federico",
                                        last_name="montesi", is_staff=True, is_superuser=True)
    user.save()

    # creazione player
    user = BaseUser.objects.create_user(email="p1@g.com", username="player", password="prova123", first_name="federico",
                                        last_name="montesi", is_player=True)
    user.save()
    player = PlayerUser.objects.create(user=user)
    player.save()
    # creazione vari croupier per avere stanze che coprono le possibili combinazioni(aperte, chiuse, vuote, piene, grandi e piccole)
    user = BaseUser.objects.create_user(email="1@g.com", username="croupier_1", password="prova123",
                                        first_name="federico", last_name="montesi", is_croupier=True)
    user.save()
    room = Room.objects.create(section=Section.objects.get(section_name="Roulette"), room_name="vuota aperta",
                               seats_number=222,
                               minimum_bet="0.10",
                               opening=time(hour=7, minute=00), closing=time(hour=23, minute=00), seats_occupied=0)
    croupier = CroupierUser(user=user, room=room)
    croupier.save()

    user = BaseUser.objects.create_user(email="2@g.com", username="croupier_2", password="prova123",
                                        first_name="federico", last_name="montesi", is_croupier=True)
    user.save()
    room = Room.objects.create(section=Section.objects.get(section_name="Roulette"), room_name="piena aperta",
                               seats_number=222, minimum_bet="0.20",
                               opening=time(hour=7, minute=00), closing=time(hour=23, minute=00), seats_occupied=222)
    croupier = CroupierUser(user=user, room=room)
    croupier.save()

    user = BaseUser.objects.create_user(email="3@g.com", username="croupier_3", password="prova123",
                                        first_name="federico", last_name="montesi", is_croupier=True)
    user.save()
    room = Room.objects.create(section=Section.objects.get(section_name="Roulette"), room_name="piena chiusa",
                               seats_number=222, minimum_bet="0.50",
                               opening=time(hour=22, minute=00), closing=time(hour=23, minute=00), seats_occupied=222)
    croupier = CroupierUser(user=user, room=room)
    croupier.save()

    user = BaseUser.objects.create_user(email="4@g.com", username="croupier_4", password="prova123",
                                        first_name="federico", last_name="montesi", is_croupier=True)
    user.save()
    room = Room.objects.create(section=Section.objects.get(section_name="Roulette"), room_name="vuota chiusa",
                               seats_number=222,
                               minimum_bet="1.00",
                               opening=time(hour=22, minute=00), closing=time(hour=23, minute=00), seats_occupied=0)
    croupier = CroupierUser(user=user, room=room)
    croupier.save()

    user = BaseUser.objects.create_user(email="5@g.com", username="croupier_5", password="prova123",
                                        first_name="federico", last_name="montesi", is_croupier=True)
    user.save()
    room = Room.objects.create(section=Section.objects.get(section_name="Roulette"), room_name="grande aperta ricca",
                               seats_number=5000,
                               minimum_bet="500.00",
                               opening=time(hour=7, minute=00), closing=time(hour=23, minute=00), seats_occupied=0)
    croupier = CroupierUser(user=user, room=room)
    croupier.save()

    user = BaseUser.objects.create_user(email="6@g.com", username="croupier_6", password="prova123",
                                        first_name="federico", last_name="montesi", is_croupier=True)
    user.save()
    room = Room.objects.create(section=Section.objects.get(section_name="Roulette"), room_name="chiusa presto povera",
                               seats_number=222,
                               minimum_bet="2.00",
                               opening=time(hour=7, minute=00), closing=time(hour=8, minute=00), seats_occupied=0)
    croupier = CroupierUser(user=user, room=room)
    croupier.save()

    user = BaseUser.objects.create_user(email="7@g.com", username="croupier_7", password="prova123",
                                        first_name="federico", last_name="montesi", is_croupier=True)
    user.save()
    room = Room.objects.create(section=Section.objects.get(section_name="Roulette"), room_name="quasi piena",
                               seats_number=222,
                               minimum_bet="10.00",
                               opening=time(hour=7, minute=00), closing=time(hour=23, minute=00), seats_occupied=221)
    croupier = CroupierUser(user=user, room=room)
    croupier.save()

    user = BaseUser.objects.create_user(email="8@g.com", username="croupier_8", password="prova123",
                                        first_name="federico", last_name="montesi", is_croupier=True)
    user.save()
    room = Room.objects.create(section=Section.objects.get(section_name="Memory"), room_name="aperta", seats_number=222,
                               minimum_bet="200.00",
                               opening=time(hour=7, minute=00), closing=time(hour=23, minute=00), seats_occupied=0)
    croupier = CroupierUser(user=user, room=room)
    croupier.save()

    user = BaseUser.objects.create_user(email="9@g.com", username="croupier_9", password="prova123",
                                        first_name="federico", last_name="montesi", is_croupier=True)
    user.save()
    room = Room.objects.create(section=Section.objects.get(section_name="Memory"), room_name="chiusa", seats_number=222,
                               minimum_bet="50.00",
                               opening=time(hour=22, minute=00), closing=time(hour=23, minute=00), seats_occupied=0)
    croupier = CroupierUser(user=user, room=room)
    croupier.save()




