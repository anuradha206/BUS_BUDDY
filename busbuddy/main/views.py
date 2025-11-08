from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import BusForm, BusDetailsForm
from .models import Bus, Route, Schedule
from django.contrib.auth.decorators import login_required

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

@login_required
def bus_register(request):
    if request.method == 'POST':
        form = BusForm(request.POST, request.FILES)
        if form.is_valid():
            bus = form.save()
            messages.success(request, 'Bus registered — continue to add seats and schedule.')
            return redirect('bus_details', pk=bus.pk)
    else:
        form = BusForm()
    return render(request, 'main/bus_register.html', {'form': form})

@login_required
def bus_details(request, pk):
    bus = get_object_or_404(Bus, pk=pk)
    if request.method == 'POST':
        form = BusDetailsForm(request.POST)
        if form.is_valid():
            bus.seats = form.cleaned_data['seats']
            bus.save()
            route = Route.objects.create(
                bus=bus,
                origin=form.cleaned_data['origin'],
                destination=form.cleaned_data['destination'],
                stops=form.cleaned_data['stops']
            )
            Schedule.objects.create(
                bus=bus,
                route=route,
                departure_time=form.cleaned_data['departure_time'],
                arrival_time=form.cleaned_data['arrival_time'],
                days=form.cleaned_data['days']
            )
            messages.success(request, 'Bus details saved.')
            return redirect('index')
    else:
        form = BusDetailsForm(initial={'seats': bus.seats})
    return render(request, 'main/bus_details.html', {'form': form, 'bus': bus})

def search_results(request):
    return render(request, 'main/bus_search.html')
