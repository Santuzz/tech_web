import os
import re

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.urls import reverse

from django.contrib.auth.models import User


class Section(models.Model):
    section_name = models.CharField(max_length=50)
    TYPE = [
        "Blackjack",
        "Poker",
        "Roulette",
        "Slot",
        "Baccarat",
        "Bingo"
    ]

    def __str__(self):
        return self.section_name


class Room(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    room_name = models.CharField(max_length=50, unique=True)
    seats_number = models.IntegerField(blank=False)
    minimum_bet = models.CharField(max_length=10, choices=[
        ("0.10", "0.10"),
        ("0.20", "0.20"),
        ("0.50", "0.50"),
        ("1.00", "1.00"),
        ("2.00", "2.00"),
        ("5.00", "5.00"),
        ("10.00", "10.00"),
        ("20.00", "20.00"),
        ("50.00", "50.00"),
        ("100.00", "100.00"),
        ("200.00", "200.00"),
        ("500.00", "500.00")
    ])
    opening = models.TimeField()  # attributo aggiunto
    closing = models.TimeField()
    seats_occupied = models.IntegerField(default=0)

    cover_pic = models.ImageField(upload_to='icon_1/', blank=True, default='room_thumbnail/room_no_thumb.png')

    class Meta:
        verbose_name_plural = 'Rooms'
        ordering = ['room_name']

    def save(self, *args, **kwargs):

        try:
            old_instance = Room.objects.filter(id=self.id)
            if old_instance[0].cover_pic:
                try:
                    if old_instance and old_instance[0].cover_pic.name != self.cover_pic.name:
                        os.remove(old_instance[0].cover_pic.path)
                except:
                    print("ROOM - Errore durante eliminazione foto precendente")
        except:
            pass
        super().save(*args, **kwargs)

    # TODO: definire un modo per ritornare i posti liberi

    def get_cover_pic_url(self):
        if hasattr(self.cover_pic, 'url'):
            return self.cover_pic.url

    def get_absolute_url(self):
        return reverse('rooms:room-overview', kwargs={'pk': self.pk})

    def __str__(self):
        return 'ROOM {} - {} - {}'.format(
            self.id, self.room_name, self.section)
