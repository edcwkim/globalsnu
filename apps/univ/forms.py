from django import forms
from .models import School


class SchoolAutodataUpdateForm(forms.ModelForm):

    class Meta:
        model = School
        fields = ['logo', 'address']
