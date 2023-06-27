import os

from django.urls import reverse
from django.core.mail import send_mail

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission
from django.db import models
from rooms.models import Room


class UserManager(BaseUserManager):
    def create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError("L'indirizzo email deve essere fornito.")
        if not username:
            raise ValueError("L'utente deve avere un username")

        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
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
    date_joined = models.DateTimeField(verbose_name='date joined', auto_now_add=True)
    last_login = models.DateTimeField(verbose_name='last login', auto_now=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_croupier = models.BooleanField('croupier status', default=False)
    is_player = models.BooleanField('player status', default=False)

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

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
        try:
            old_instance = BaseUser.objects.filter(id=self.id)
            if old_instance[0].profile_pic:
                try:
                    if old_instance and old_instance[0].profile_pic.name != self.profile_pic.name:
                        os.remove(old_instance[0].profile_pic.path)
                except:
                    print("ACCOUNT - Errore durante eliminazione foto precendente")
        except:
            pass
        super().save(*args, **kwargs)

    def get_profile_pic_url(self):
        if self.profile_pic and hasattr(self.profile_pic, 'url'):
            return self.profile_pic.url
        else:
            return '/static/img/profile_no_pic.jpg'

    def get_absolute_url(self):
        return reverse('user_mgmt:profile', kwargs={'pk': self.pk})

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)


class PlayerUser(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True, related_name="player")
    rooms = models.ManyToManyField(Room, through="RoomPlayer")
    saldo = models.FloatField(default=0)

    def __str__(self):
        return 'PLAYER - {} - {}'.format(self.user.id, self.user.username)


class CroupierUser(models.Model):
    user = models.OneToOneField(BaseUser, on_delete=models.CASCADE, primary_key=True, related_name="croupier")
    room = models.OneToOneField(Room, on_delete=models.CASCADE, related_name='croupier_room', null=True)

    def __str__(self):
        return 'CROUPIER - {} - {}'.format(self.user.id, self.user.username)


class RoomPlayer(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="room_player")
    player = models.ForeignKey(PlayerUser, on_delete=models.CASCADE, related_name="player_room")

    def save(self, *args, **kwargs):
        self.room.seats_occupied = self.room.room_player.count()  # Update seats_occupied when saving
        self.room.save()  # Save the room object
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.room.seats_occupied = self.room.room_player.count() - 1  # Update seats_occupied when deleting
        self.room.save()  # Save the room object
        super().delete(*args, **kwargs)