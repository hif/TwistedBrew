from django import forms
from django.forms import ModelForm
from django.forms.formsets import formset_factory
from models import Session, SessionDetail


class SessionForm(ModelForm):

    class Meta:
        model = Session


SessionFormSet = formset_factory(SessionForm)


class SessionDetailForm(ModelForm):

    class Meta:
        model = SessionDetail
        fields = ['name', 'worker', 'target', 'hold_time', 'time_unit_seconds', 'notes', 'done']
