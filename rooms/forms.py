from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
import re

from .models import Room
from django.db import transaction


class RoomCreationForm(forms.ModelForm):
    helper = FormHelper()
    helper.add_input(
        Submit('submit', 'Salva', css_class='btn btn-success')
    )
    opening = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M'),
        input_formats=['%H:%M'],
    )
    closing = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M'),
        input_formats=['%H:%M'],
    )
    opening.label = "Orario di apertura"
    closing.label = "Orario di chiusura"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['opening'].widget.attrs['placeholder'] = 'HH:MM'
        self.fields['closing'].widget.attrs['placeholder'] = 'HH:MM'

    def clean(self):
        # TODO non funziona il controllo del nome della stanza, bisogna include anche l'apostrofo
        re_name = r'^[a-zA-ZÀ-ÿ\'\s]+$'
        seats_number = self.cleaned_data.get('seats_number')
        room_name = self.cleaned_data.get('room_name')
        opening = self.cleaned_data.get('opening')
        closing = self.cleaned_data.get('closing')
        if not re.match(re_name, room_name):
            raise forms.ValidationError("Il nome della stanza non può contenere caratteri speciali")
        if seats_number > 5000 or seats_number < 1:
            raise forms.ValidationError("Capienza inserita non valida")
        if (not opening) or (not closing):
            raise forms.ValidationError("L'orario inserito non è valido")
        if opening > closing:
            raise forms.ValidationError("L'orario di chiusura deve essere successiva all'orario di apertura")
        cleaned_data = super(forms.ModelForm, self).clean()
        return cleaned_data

    @transaction.atomic
    def save(self):
        room = super().save(commit=False)
        room.save()
        return room

    class Meta:
        model = Room
        fields = (
            "section",
            "room_name",
            "seats_number",
            "minimum_bet",
            "opening",
            "closing",
            "cover_pic"
        )
        labels = {
            'section': 'Sezione',
            'room_name': 'Nome',
            'seats_number': 'Capienza massima (max 5000)',
            'minimum_bet': 'Puntata minima permessa',
            'opening': 'Orario di apertura',
            'closing': 'Orario di chiusura',
            'cover_pic': 'Immagine di copertina',
        }


class SubmitButtonMixin(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Create', css_class='btn btn-success'))

        if self.instance.id:
            self.helper.inputs[0].value = 'Update'
            self.helper.inputs[0].field_classes = 'btn btn-warning'
