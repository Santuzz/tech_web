import os
import re

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.urls import reverse

from django.db.models.signals import post_delete
from django.dispatch import receiver

from django.contrib.auth.models import User


class Section(models.Model):
    section_name = models.CharField(max_length=50)
    TYPE = [
        "Roulette",
        "memory",
        "Slot",

    ]

    def __str__(self):
        return self.section_name


@receiver(post_delete, sender=Section)
def delete_user(sender, instance, using, **kwargs):
    rooms = Room.objects.filter(section__section_name=instance.section_name)
    for room in rooms:
        room.delete()


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

    cover_pic = models.ImageField(upload_to='room_thumbnail/', blank=True, default='room_thumbnail/room_no_thumb.png')

    class Meta:
        verbose_name_plural = 'Rooms'
        ordering = ['room_name']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def get_cover_pic_url(self):
        if self.cover_pic and hasattr(self.cover_pic, 'url'):
            return self.cover_pic.url
        else:
            return 'room_thumbnail/room_no_thumb.png'

    def get_absolute_url(self):
        return reverse('rooms:room-overview', kwargs={'pk': self.pk})

    def get_minimum_bet(self):
        return float(self.minimum_bet)

    def is_subscribable(self):
        return self.seats_number > self.seats_occupied

    def __str__(self):
        return 'ROOM {} - {} - {}'.format(
            self.id, self.room_name, self.section)
