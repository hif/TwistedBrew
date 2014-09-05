from django import forms
from django.forms import ModelForm
from django.forms.formsets import formset_factory
from web.models import Session


class CommanderForm(forms.Form):
    command = forms.CharField(label="Command:", max_length=128, initial="Please enter a command...")


class SessionForm(ModelForm):

    class Meta:
        model = Session
        fields = ['name', 'session_date', 'source', 'notes', 'locked']

SessionFormSet = formset_factory(SessionForm)