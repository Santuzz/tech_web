from rooms.models import Room, Section

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
    Room.objects.all().delete()
    Section.objects.all().delete()


"""def init_db():
    section = [
        "Blackjack",
        "Poker",
        "Roulette",
        "Slot",
        "Baccarat",
        "Bingo"
    ]
    if len(Room.objects.all()) != 0:
        return

    # se è vuoto lo inizializzo
    count = 1
    cover_pics = [models.ImageField(upload_to=path, null=True, blank=True) for path in get_valid_upload_paths(count)]

    roomdict = {
        "section": [],
        "room_name": [
            "Palazzo delle Illusioni", "Regno delle Perdite Assicurate", "Covo dei Sogni Infranti",
            "Sala degli Sprechi Imminenti", "Stanze della Disperazione", "Santuario dei Portafogli Vuoti",
            "Rovine del Denaro Facile", "Casinò della Fortuna Inesistente", "Dimora delle Probabilità Infime",
            "Labirinto dell'Inganno Finanziario", "Oasi delle Spese Imprevedibili", "Torre dei Soldi Fuggenti",
            "Carcere delle Aspettative Fallite", "Spazio dei Miraggi Vincenti", "Grotta delle Scommesse Insensate",
            "Tempio delle Disgrazie Finanziarie", "Reggia del Denaro Svanito", "Cripta dei Risparmi Evaporati",
            "Cittadella delle Truffe Sottili", "Sala delle Pseudovittorie", "Rifugio delle Fregature Certe",
            "Casinò dell'Incertezza Eterna", "Bazar delle False Promesse", "Ludoteca dei Guadagni Effimeri",
            "Rovine della Rendita Impossibile", "Stanza dell'Oblio Finanziario", "Santuario dei Piani Falliti",
            "Covo degli Indebitati Perpetui", "Fondazione della Malasorte", "Sala dell'Impazienza Finanziaria",
            "Gabbia dei Desideri Illusori"
        ],
        "seats_number": [
            1345, 2567, 3891, 4234, 5678, 6981, 7210, 8456, 9632, 10000, 1357, 2468, 3579, 4680, 5791, 6902, 8013, 9124,
            4231, 5678, 1345, 2567, 3891, 4234, 5678, 6981, 7210, 8456, 9632, 10000
        ],
        "minimum_bet": [
            "0.10", "0.20", "0.50", "1.00", "2.00", "5.00", "10.00", "20.00", "50.00", "100.00", "200.00", "500.00"
        ],
        "opening": [
            time(hour=i % 13, minute=i * 5 % 60) for i in range(30)
        ],
        "closing": [
            time(hour=i % 11 + 13, minute=i * 5 % 60) for i in range(30)
        ],
        "cover_pic": [
            "room_thumbnail/immagine_1045_0.jpg", "room_thumbnail/immagine_1047_0.jpg",
            "room_thumbnail/immagine_1109_0.jpg", "room_thumbnail/immagine_1111_0.jpg",
            "room_thumbnail/immagine_1113_0.jpg", "room_thumbnail/immagine_1117_0.jpg",
            "room_thumbnail/immagine_1125_0.jpg", "room_thumbnail/immagine_1128_0.jpg",
            "room_thumbnail/immagine_1131_0.jpg", "room_thumbnail/immagine_1134_0.jpg",
            "room_thumbnail/immagine_1137_0.jpg", "room_thumbnail/immagine_1140_0.jpg",
            "room_thumbnail/immagine_1143_0.jpg", "room_thumbnail/immagine_1149_0.jpg",
            "room_thumbnail/immagine_1153_0.jpg", "room_thumbnail/immagine_1162_0.jpg",
            "room_thumbnail/immagine_1165_0.jpg", "room_thumbnail/immagine_1170_0.jpg",
            "room_thumbnail/immagine_1173_0.jpg", "room_thumbnail/immagine_1183_0.jpg",
            "room_thumbnail/immagine_1325_0.jpg", "room_thumbnail/immagine_1418_0.jpg",
            "room_thumbnail/immagine_1548_0.jpg", "room_thumbnail/immagine_1564_0.jpg",
            "room_thumbnail/immagine_1573_0.jpg", "room_thumbnail/immagine_1579_0.jpg",
            "room_thumbnail/immagine_1585_0.jpg", "room_thumbnail/immagine_1626_0.jpg",
            "room_thumbnail/immagine_1630_0.jpg", "room_thumbnail/immagine_1632_0.jpg",
            "room_thumbnail/immagine_1633_0.jpg", "room_thumbnail/immagine_1634_0.jpg",
            "room_thumbnail/immagine_1635_0.jpg", "room_thumbnail/immagine_1636_0.jpg",
            "room_thumbnail/immagine_1638_0.jpg", "room_thumbnail/immagine_1656_0.jpg",
            "room_thumbnail/immagine_1659_0.jpg", "room_thumbnail/immagine_1660_0.jpg",
            "room_thumbnail/immagine_1661_0.jpg", "room_thumbnail/immagine_1662_0.jpg",
            "room_thumbnail/immagine_1663_0.jpg", "room_thumbnail/immagine_1665_0.jpg",
            "room_thumbnail/immagine_1666_0.jpg", "room_thumbnail/immagine_1667_0.jpg",
            "room_thumbnail/immagine_1668_0.jpg", "room_thumbnail/immagine_1669_0.jpg",
            "room_thumbnail/immagine_1670_0.jpg", "room_thumbnail/immagine_1671_0.jpg",
            "room_thumbnail/immagine_1673_0.jpg", "room_thumbnail/immagine_1675_0.jpg",
            "room_thumbnail/immagine_1676_0.jpg", "room_thumbnail/immagine_1678_0.jpg",
            "room_thumbnail/immagine_1680_0.jpg", "room_thumbnail/immagine_1682_0.jpg",
            "room_thumbnail/immagine_1686_0.jpg", "room_thumbnail/immagine_1687_0.jpg",
            "room_thumbnail/immagine_1688_0.jpg", "room_thumbnail/immagine_1689_0.jpg",
            "room_thumbnail/immagine_1690_0.jpg", "room_thumbnail/immagine_1691_0.jpg",
            "room_thumbnail/immagine_1692_0.jpg", "room_thumbnail/immagine_1695_0.jpg",
            "room_thumbnail/immagine_1696_0.jpg", "room_thumbnail/immagine_1697_0.jpg",
            "room_thumbnail/immagine_1700_0.jpg", "room_thumbnail/immagine_1713_0.jpg",
            "room_thumbnail/immagine_1715_0.jpg", "room_thumbnail/immagine_1716_0.jpg",
            "room_thumbnail/immagine_1724_0.jpg", "room_thumbnail/immagine_1725_0.jpg",
            "room_thumbnail/immagine_1732_0.jpg", "room_thumbnail/immagine_1734_0.jpg",
            "room_thumbnail/immagine_1735_0.jpg", "room_thumbnail/immagine_1758_0.jpg",
            "room_thumbnail/immagine_1760_0.jpg", "room_thumbnail/immagine_1761_0.jpg",
            "room_thumbnail/immagine_1762_0.jpg", "room_thumbnail/immagine_1765_0.jpg",
            "room_thumbnail/immagine_1766_0.jpg", "room_thumbnail/immagine_1768_0.jpg",
            "room_thumbnail/immagine_1775_0.jpg", "room_thumbnail/immagine_1799_0.jpg",
            "room_thumbnail/immagine_1803_0.jpg", "room_thumbnail/immagine_1808_0.jpg",
            "room_thumbnail/immagine_1813_0.jpg", "room_thumbnail/immagine_1815_0.jpg",
            "room_thumbnail/immagine_1819_0.jpg", "room_thumbnail/immagine_1826_0.jpg",
            "room_thumbnail/immagine_1828_0.jpg", "room_thumbnail/immagine_1832_0.jpg",
            "room_thumbnail/immagine_1835_0.jpg", "room_thumbnail/immagine_1837_0.jpg"
        ]

    }
    s = []
    r = 0
    for i in range(len(section)):
        s.append(Section())
        s[i].section_name = section[i]
        s[i].save()

    for i in range(len(roomdict.get("room_name"))):
        r = Room()
        for k in roomdict:
            if k == "section":
                if 0 <= i <= 4:
                    r.section = s[0]
                elif 5 <= i <= 9:
                    r.section = s[1]
                elif 10 <= i <= 14:
                    r.section = s[2]
                elif 15 <= i <= 19:
                    r.section = s[3]
                elif 20 <= i <= 24:
                    r.section = s[4]
                elif 25 <= i <= 29:
                    r.section = s[5]
                else:
                    return None
            elif k == "room_name":
                r.room_name = roomdict[k][i]
            elif k == "seats_number":
                r.seats_number = roomdict[k][i]

            elif k == "minimum_bet":
                random_index = random.randint(0, len(roomdict[k]) - 1)
                r.minimum_bet = roomdict[k][random_index]
            elif k == "opening":
                r.opening = roomdict[k][i]
            elif k == "closing":
                r.closing = roomdict[k][i]
            elif k == "cover_pic":
                random_index = random.randint(0, len(roomdict[k]) - 1)
                r.cover_pic = roomdict[k][random_index]
        r.save()
"""

