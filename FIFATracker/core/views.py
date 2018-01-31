from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages

from .models import CareerSaveFileModel
from .forms import CareerSaveFileForm

def upload_career_save_file(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Only authenticated users are allowed to upload files.')
        return redirect('home')

    # Check if user already uploaded a file and it's not processed yet
    if CareerSaveFileModel.objects.filter(user_id=request.user.id):
        messages.error(request, "You cannot upload new file if the previous one hasn't been processed.")
        return render(request, 'upload.html', {'upload_completed': True} )   

    if request.method == 'POST':
        form = CareerSaveFileForm(request.POST, request.FILES)
        if form.is_valid():
            form = form.save(commit=False)
            form.user = request.user
            form.save()
            messages.success(request, "Upload completed.")
            return render(request, 'upload.html', {'upload_completed': True} )   
    else:
        form = CareerSaveFileForm()

    return render(request, 'upload.html', {'form':form})    

def privacypolicy(request):
    return render(request, 'privacy.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def donate(request):
    return render(request, 'donate.html')

def home(request):
    return render(request, 'home.html')