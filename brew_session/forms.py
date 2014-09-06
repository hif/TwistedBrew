from django import forms
from django.forms import ModelForm
from django.forms.formsets import formset_factory
from models import Session


class SessionForm(ModelForm):

    class Meta:
        model = Session
        #fields = ['name', 'session_date', 'source', 'notes', 'locked']

SessionFormSet = formset_factory(SessionForm)