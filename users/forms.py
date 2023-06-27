from crispy_forms.bootstrap import FieldWithButtons, StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Row, Column
from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm
from django.forms.widgets import HiddenInput

from .models import PlayerUser, CroupierUser, BaseUser
from django.db import transaction


class PlayerUserCreationForm(UserCreationForm):
    helper = FormHelper()
    helper.add_input(Layout(
        Submit('submit', 'Register', css_class="btn btn-success"),

    )

    )
    helper.form_method = 'POST'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['email'].widget.attrs['placeholder'] = 'example@example.com'
        self.fields['password2'].widget.attrs['placeholder'] = 'ripeti la password inserita'

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_player = True
        user.save()
        return user

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if BaseUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Username già in uso. Scegli un altro username.")
        return username

    class Meta:
        model = BaseUser
        fields = (
            'username',
            'email',
            'password1',
            'password2',
            'first_name',
            'last_name',
            'profile_pic',
        )
        labels = {
            'username': 'Nome Utente',
            'first_name': 'Nome',
            'last_name': 'Cognome',
            'profile_pic': 'Immagine profilo',
        }


class CroupierUserCreationForm(UserCreationForm):
    helper = FormHelper()
    helper.add_input(
        Submit('submit', 'Register', css_class="btn btn-success")
    )
    helper.form_method = 'POST'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.fields['username'].widget.attrs['placeholder'] = 'username'
        self.fields['email'].widget.attrs['placeholder'] = 'example@example.com'
        self.fields['password2'].widget.attrs['placeholder'] = 'ripeti la password inserita'

    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_croupier = True
        user.save()
        return user

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if BaseUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Username già in uso. Scegli un altro username.")
        return username

    class Meta:
        model = BaseUser
        fields = (
            'username',
            'email',
            'password1',
            'password2',
            'first_name',
            'last_name',
        )
        labels = {
            'username': 'Nome Utente',
            'first_name': 'Nome',
            'last_name': 'Cognome',
        }
