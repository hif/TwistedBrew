from django import forms

class CommanderForm(forms.Form):
    command = forms.CharField(label="Command:", max_length=128)