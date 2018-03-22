from django import forms
from .models import CareerSaveFileModel

class CareerSaveFileForm(forms.ModelForm):        
    class Meta:
        model = CareerSaveFileModel
        fields = ('uploadedfile', 'fifa_edition')
