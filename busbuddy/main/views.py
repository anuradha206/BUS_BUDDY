from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages

def index(request):
    return render(request, 'main/index.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
            messages.success(request, 'Account created — you are now logged in.')
            return redirect('index')
        # if invalid, fall through to render with the bound form (shows errors)
    else:
        form = UserCreationForm()
    return render(request, 'main/register.html', {'form': form})