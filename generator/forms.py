from django import forms
from .models import IncidentPlaybook, CustomStep

class PlaybookForm(forms.ModelForm):
    class Meta:
        model = IncidentPlaybook
        fields = ['incident_type', 'severity', 'affected_systems']


class CustomStepForm(forms.ModelForm):
    class Meta:
        model = CustomStep
        fields = ['step_description', 'step_order']

CustomStepFormSet = forms.inlineformset_factory(IncidentPlaybook, CustomStep, form=CustomStepForm, extra=1)