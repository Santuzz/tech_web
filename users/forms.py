from crispy_forms.bootstrap import FieldWithButtons, StrictButton
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Row, Column, HTML
from django import forms
from django.contrib.auth.forms import UserCreationForm, SetPasswordForm, UserModel
from django.forms.widgets import HiddenInput

from .models import PlayerUser, CroupierUser, BaseUser
from django.db import transaction


class UserUpdatePicForm(forms.ModelForm):
    helper = FormHelper()
    helper.form_method = 'POST'
    helper.layout = Layout(
        'profile_pic',
        HTML(
            """<div id="display-image"></div>
            <hr>""", ),
        Submit('submit', 'Salva', css_class="btn btn-success"),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        pic = super().save(commit=False)
        pic.save()
        return pic

    class Meta:
        model = BaseUser
        fields = (
            'profile_pic',
        )
        labels = {
            'profile_pic': 'Immagine profilo',
        }


class PlayerUserCreationForm(UserCreationForm):
    helper = FormHelper()
    helper.form_method = 'POST'
    helper.add_input(
        Submit('submit', 'Salva', css_class='btn btn-success')
    )

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
        )
        labels = {
            'username': 'Nome Utente',
            'first_name': 'Nome',
            'last_name': 'Cognome',
        }


class CroupierUserCreationForm(UserCreationForm):
    helper = FormHelper()
    helper.form_method = 'POST'
    helper.add_input(
        Submit('submit', 'Salva', css_class='btn btn-success')
    )

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
