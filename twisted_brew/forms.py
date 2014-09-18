from django import forms
from django.forms import ModelForm
from django.forms.formsets import formset_factory

class CommanderForm(forms.Form):
    command = forms.CharField(label="Command:", max_length=128, initial="Please enter a command...")

