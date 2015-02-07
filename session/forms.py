from django import forms
from django.forms import ModelForm
from django.forms.formsets import formset_factory
from session.models import Session, SessionDetail


class SessionForm(ModelForm):

    class Meta:
        model = Session
        fields = ['name', 'session_date', 'source', 'notes']

    def save(self, commit=True):
        instance = super(ModelForm, self).save(commit=False)
        if commit:
            instance.save()
        return instance


SessionFormSet = formset_factory(SessionForm)


class SessionDetailForm(ModelForm):

    class Meta:
        model = SessionDetail
        fields = ['name', 'worker_type', 'target', 'hold_time', 'time_unit_seconds', 'notes', 'done']
