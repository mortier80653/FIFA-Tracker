from django import forms
from .models import CareerSaveFileModel

class CareerSaveFileForm(forms.ModelForm):        
    class Meta:
        model = CareerSaveFileModel
        exclude = ('user',)
        fields = ('uploadedfile',)
