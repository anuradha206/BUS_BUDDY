from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import BusForm, BusDetailsForm, BusSearchForm, ConductorForm
from .models import Bus, Route, Schedule, Conductor
from django.contrib.auth.decorators import login_required
try:
    from main.models import Booking  # optional, keep if Booking exists
except Exception:
    Booking = None

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



@login_required(login_url='login')
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
            # main model uses total_seats; update that
            bus.total_seats = form.cleaned_data['seats']
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
        form = BusDetailsForm(initial={'seats': bus.total_seats})
    return render(request, 'main/bus_details.html', {'form': form, 'bus': bus})
def search_buses(request):
    form = BusSearchForm(request.GET or None)
    schedules = Schedule.objects.none()

    if form.is_valid():
        source = form.cleaned_data['source']
        destination = form.cleaned_data['destination']
        bus_type = form.cleaned_data['bus_type']
        sleeper_type = form.cleaned_data['sleeper_type']
        is_woman_safe = form.cleaned_data['is_woman_safe']

        # start with all schedules and filter in Python by stop order
        candidates = Schedule.objects.select_related('bus', 'route').all()

        filtered = []
        for sched in candidates:
            route = sched.route
            if not route:
                continue

            # build ordered stop list: origin + stops + destination
            stops_seq = [route.origin]
            if route.stops:
                stops_seq += [s.strip() for s in route.stops.split(',') if s.strip()]
            stops_seq.append(route.destination)

            # find source and destination occurrences (case-insensitive substring match)
            def find_index(term):
                term_l = term.lower()
                for i, v in enumerate(stops_seq):
                    if term_l in v.lower():
                        return i
                return None

            i = find_index(source)
            j = find_index(destination)
            if i is None or j is None or i >= j:
                continue

            # apply bus-level filters
            bus = sched.bus
            if bus_type:
                if bus_type == 'AC' and not bus.is_ac:
                    continue
                if bus_type == 'Non-AC' and bus.is_ac:
                    continue
            if sleeper_type:
                if sleeper_type == 'Sleeper' and not bus.is_sleeper:
                    continue
                if sleeper_type == 'Seater' and bus.is_sleeper:
                    continue
            if is_woman_safe and not bus.is_women_safe:
                continue

            filtered.append(sched)

        schedules = filtered

    # render main search results template (uses 'schedules' variable)
    return render(request, 'main/search_results.html', {
        'form': form,
        'schedules': schedules,
        'origin': request.GET.get('source', ''),
        'destination': request.GET.get('destination', ''),
    })
def search_results(request):
    return render(request, 'main/bus_search.html')
def sectors(request):
    return render(request, 'main/sectors.html')
def connected(request):
    return render(request, 'main/connected.html')
def who_we_are(request):
    return render(request, 'main/who_we_are.html')

@login_required(login_url='login')
def search(request):
    return render(request, 'main/search.html')


@login_required(login_url='login')
def conductor_register(request):
    """Register a conductor profile for the logged-in user."""
    conductor = getattr(request.user, 'conductor', None)
    if conductor is not None:
        messages.info(request, 'You are already registered as a conductor.')
        return redirect('register_bus')

    if request.method == 'POST':
        form = ConductorForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.user = request.user
            c.save()
            messages.success(request, 'Conductor profile created. You can now register your bus.')
            return redirect('register_bus')
    else:
        form = ConductorForm()
    return render(request, 'main/conductor_register.html', {'form': form})


def register_bus(request):
    # Require login and conductor account
    from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def register_bus(request):
    # ensure user has a Conductor profile
    conductor = getattr(request.user, 'conductor', None)
    if conductor is None:
        return redirect('conductor_register')

    if request.method == "POST":
        bus_name = request.POST.get("bus_name")
        registration_number = request.POST.get("bus_number")
        from_city = request.POST.get("from_city")
        to_city = request.POST.get("to_city")
        total_seats = request.POST.get("total_seats")
        departure_time = request.POST.get("departure_time")

        # this gets all stops[] fields as a list
        stops_list = request.POST.getlist("stops[]")

        # convert to comma-separated string
        stops_string = ",".join([stop.strip() for stop in stops_list if stop.strip() != ""])

        # create bus and associate conductor
        bus = Bus.objects.create(
            bus_name=bus_name,
            registration_number=registration_number,
            total_seats=total_seats,
            conductor=conductor,
        )

        # create route
        route = Route.objects.create(
            bus=bus,
            origin=from_city,
            destination=to_city,
            stops=stops_string
        )

        # create schedule (arrival time not included in your form)
        Schedule.objects.create(
            bus=bus,
            route=route,
            departure_time=departure_time,
            arrival_time="00:00",  # placeholder until you add field
            days="Mon,Tue,Wed",    # placeholder
        )

        return redirect("index")

    return render(request, "main/register_bus.html")

@login_required(login_url='login')
def bookings(request):
    return render(request, 'main/bookings.html')