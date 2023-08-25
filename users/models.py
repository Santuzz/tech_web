from django.urls import reverse
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from rooms.models import Room
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.db import connection


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("L'indirizzo email deve essere fornito.")
        if not username:
            raise ValueError("L'utente deve avere un username")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        if not connection.settings_dict['TEST']:
            if user.is_player:
                PlayerUser.objects.get_or_create(user=user)
            elif user.is_croupier:
                CroupierUser.objects.get_or_create(user=user)
            user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password, **extra_fields):
        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            username=username
        )

        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class BaseUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=30, unique=True)
    date_joined = models.DateTimeField(verbose_name='date joined', default=timezone.now)
    last_login = models.DateTimeField(verbose_name='last login', default=timezone.now)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_croupier = models.BooleanField('croupier status', default=False)
    is_player = models.BooleanField('player status', default=False)

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True,
                                    default='profile_pics/profile_no_pic.jpg')

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'password', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'utente'
        verbose_name_plural = 'utenti'
        swappable = 'AUTH_USER_MODEL'

    def has_module_perms(self, app_Label):
        return True

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)

    def get_profile_pic_url(self):
        if self.profile_pic and hasattr(self.profile_pic, 'url'):
            return self.profile_pic.url
        else:
            return 'profile_pics/profile_no_pic.jpg'

    def get_absolute_url(self):
        return reverse('user_mgmt:profile', kwargs={'pk': self.pk})

    def __str__(self):
        return 'USER - {} - {}'.format(self.id, self.username)


class PlayerUser(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True, related_name="player")
    rooms = models.ManyToManyField(Room, through="RoomPlayer")
    saldo = models.FloatField(default=0)

    def __str__(self):
        return 'PLAYER - {} - {}'.format(self.user.id, self.user.username)


@receiver(post_delete, sender=PlayerUser)
def delete_user(sender, instance, using, **kwargs):
    instance.user.delete()


class Giocata(models.Model):
    player = models.ForeignKey('PlayerUser', on_delete=models.CASCADE, related_name='giocate')
    timestamp = models.DateTimeField(default=timezone.now)
    importo = models.FloatField()
    room = models.CharField(default="", max_length=255)
    is_ricarica = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        saldo = self.player.saldo + self.importo
        self.player.saldo = round(saldo, 2)
        self.player.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Giocata - Player: {self.player.user_id}, Timestamp: {self.timestamp}, Importo: {self.importo}'

    class Meta:
        verbose_name = 'giocata'
        verbose_name_plural = 'giocate'


class CroupierUser(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True, related_name="croupier")
    room = models.OneToOneField(Room, on_delete=models.SET_NULL, related_name='croupier_room', null=True, blank=True)

    def __str__(self):
        return 'CROUPIER - {} - {}'.format(self.user.id, self.user.username)


@receiver(post_delete, sender=CroupierUser)
def delete_user(sender, instance, using, **kwargs):
    instance.user.delete()
    if instance.room:
        instance.room.delete()


class RoomPlayer(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="room_player")
    player = models.ForeignKey(PlayerUser, on_delete=models.CASCADE, related_name="player_room")

    def save(self, *args, **kwargs):
        if self.room.seats_occupied < self.room.seats_number:
            self.room.seats_occupied = self.room.room_player.count()
            self.room.save()

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.room.seats_occupied = self.room.room_player.count() - 1
        self.room.save()
        super().delete(*args, **kwargs)

    def __str__(self):
        return 'RP - {} - {}'.format(self.room_id, self.player_id)

    class Meta:
        unique_together = ('room', 'player')
