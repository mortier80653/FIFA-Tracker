from django.shortcuts import render, redirect
from django.conf import settings

from .models import CareerSaveFileModel
from .forms import CareerSaveFileForm

def upload_career_save_file(request):

    # Check if user already uploaded a file and it's not processed yet
    if CareerSaveFileModel.objects.filter(user_id=request.user.id):
        return render(request, 'upload.html', {'upload_completed': True} )   

    if request.method == 'POST':
        form = CareerSaveFileForm(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.save()
            return render(request, 'upload.html', {'upload_completed': True} )   
    else:
        form = CareerSaveFileForm()

    return render(request, 'upload.html', {'form':form})    

def privacypolicy(request):
    return render(request, 'privacy.html')

def home(request):
    return render(request, 'home.html')