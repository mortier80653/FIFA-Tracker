from django import forms
from file_uploads.models import CareerSaveFileModel


class CareerSaveFileForm(forms.ModelForm):
    class Meta:
        model = CareerSaveFileModel
        fields = ('uploadedfile', 'fifa_edition')
