# main/views.py
from collections import Counter
from datetime import datetime, time as dtime, timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.contrib.auth import logout
from .forms import UserRegisterForm, User


from .forms import BusDetailsForm, BusForm, BusSearchForm, ConductorForm
from .models import (
    Booking,
    Bus,
    Conductor,
    Payment,

    Stop,
    Route,
    Schedule,
    seats_available,
)


def index(request):
    return render(request, "main/index.html")



def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data.get('email')

            # If user already exists
            if User.objects.filter(username=email).exists():
                messages.error(request, "This email is already registered.")
                return redirect('register')

            form.save()
            messages.success(request, "Account created successfully.")
            return redirect('login')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegisterForm()

    return render(request, 'main/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect("index")
        else:
            messages.error(request, "Incorrect email or password")

    return render(request, "main/login.html")


@login_required(login_url="login")
def bus_register(request):
    """
    Page for authenticated users to create a Bus (using BusForm).
    After creating a bus, redirect to bus_details to add route/schedule info.
    """
    if request.method == "POST":
        form = BusForm(request.POST, request.FILES)
        if form.is_valid():
            bus = form.save(commit=False)
            # if you want to attach conductor automatically do that elsewhere
            bus.save()
            messages.success(request, "Bus registered — continue to add seats and schedule.")
            return redirect("bus_details", pk=bus.pk)
    else:
        form = BusForm()
    return render(request, "main/bus_register.html", {"form": form})


@login_required
def bus_details(request, pk):
    bus = get_object_or_404(Bus, pk=pk)

    if request.method == "POST":
        form = BusDetailsForm(request.POST)
        if form.is_valid():
            seats = form.cleaned_data["seats"]
            origin = form.cleaned_data["origin"]
            destination = form.cleaned_data["destination"]
            stops_raw = form.cleaned_data["stops"]
            departure = form.cleaned_data["departure_time"]
            arrival = form.cleaned_data["arrival_time"]
            days_selected = form.cleaned_data["days"]

            stops_list = [s.strip() for s in stops_raw.split(",") if s.strip()]
            stop_times = request.POST.getlist("stop_times[]")

            if isinstance(days_selected, list):
                days_value = ",".join(days_selected)
            else:
                days_value = days_selected

            with transaction.atomic():
                bus.total_seats = seats
                bus.ac_type = form.cleaned_data["ac_type"]
                bus.bus_type = form.cleaned_data["bus_type"]
                # Update is_sleeper based on bus_type
                bus.is_sleeper = (form.cleaned_data["bus_type"] == "Sleeper")
                bus.save()

                route = Route.objects.create(
                    bus=bus,
                    origin=origin,
                    destination=destination,
                    stops=stops_raw,
                )

                for idx, stop_name in enumerate(stops_list):
                    time_str = stop_times[idx] if idx < len(stop_times) else "00:00"
                    try:
                        stop_time = datetime.strptime(time_str, "%H:%M").time()
                    except:
                        stop_time = dtime(0, 0)

                    Stop.objects.create(
                        route=route,
                        name=stop_name,
                        time=stop_time,
                        order=idx,
                    )

                Schedule.objects.create(
                    bus=bus,
                    route=route,  # Now this works
                    departure_time=departure,
                    arrival_time=arrival,
                    days=days_value,
                )

            messages.success(request, "Bus details saved.")
            return redirect("conductor_dashboard")

    else:
        form = BusDetailsForm(initial={"seats": bus.total_seats})

    return render(request, "main/bus_details.html", {"form": form, "bus": bus})

def _schedule_to_context(sched):
    """
    Convert a Schedule instance into a simple dict structure.
    """
    route = sched.route if sched.route else None
    bus = sched.bus
    available = seats_available(sched)
    
    # Calculate duration
    duration = get_duration(sched.departure_time, sched.arrival_time)
    
    # Calculate price
    price = calculate_price(route, bus) if route else 0
    
    return {
        "id": sched.pk,
        "bus": {
            "name": getattr(bus, "bus_name", str(bus)),
            "registration_number": getattr(bus, "registration_number", ""),
            "ac_type": getattr(bus, "ac_type", ""),
            "bus_type": getattr(bus, "bus_type", ""),
            "is_sleeper": getattr(bus, "is_sleeper", False),
            "driver_name": getattr(bus, "driver_name", ""),
        },
        "route": {
            "start": getattr(route, "origin", "") if route else "",
            "end": getattr(route, "destination", "") if route else "",
            "stops": getattr(route, "stops", "") if route else "",
        },
        "date": sched.date.strftime("%Y-%m-%d") if sched.date else "",
        "time": sched.departure_time.strftime("%H:%M"),
        "arrival_time": sched.arrival_time.strftime("%H:%M"),
        "days": sched.days or "",
        "available": available,
        "duration": duration,
        "price": price,
        "raw_schedule": sched,
    }

def search_buses(request):
    """
    Search schedules that match source, destination, and date/day criteria.
    Handle both new and old parameter names.
    """
    form = BusSearchForm(request.GET or None)
    schedules_ctx = []
    
    # Handle both parameter naming conventions
    source = request.GET.get('source') or request.GET.get('from_place', '')
    destination = request.GET.get('destination') or request.GET.get('to_place', '')
    travel_date = request.GET.get('travel_date')
    day_filter = request.GET.get('Day') or request.GET.get('day_filter', '')
    
    # If form is valid or we have search parameters
    if form.is_valid() or source or destination:
        source = source.strip().lower()
        destination = destination.strip().lower()
        
        # Handle travel_date if provided
        travel_date_obj = None
        if travel_date:
            try:
                travel_date_obj = datetime.strptime(travel_date, "%Y-%m-%d").date()
                # Get day name from date
                day_from_date = travel_date_obj.strftime("%A")  # Monday, Tuesday, etc.
                day_abbr_from_date = travel_date_obj.strftime("%a")  # Mon, Tue, etc.
            except ValueError:
                travel_date_obj = None
                day_from_date = None
                day_abbr_from_date = None
        
        # Handle day filter if provided
        day_abbr = None
        if day_filter:
            day_name_map = {
                'Monday': 'Mon' or 'mon' or 'monday', 'Tuesday': 'Tue' or 'tue' or 'tuesday', 'Wednesday': 'Wed' or 'wed' or 'wednesday',
                'Thursday': 'Thu' or 'tue' or 'tuesday', 'Friday': 'Fri' or 'fri' or 'friday', 'Saturday': 'Sat' or 'sat' or 'saturday', 'Sunday': 'Sun' or 'sun' or 'sunday'
            }
            day_abbr = day_name_map.get(day_filter, day_filter[:3])
        
        # Determine which day to use (priority: travel_date > Day filter)
        target_day_abbr = None
        if travel_date_obj and day_abbr_from_date:
            target_day_abbr = day_abbr_from_date
        elif day_abbr:
            target_day_abbr = day_abbr
        
        # Get all schedules with related data
        candidates = Schedule.objects.select_related("bus", "route").all()
        
        for sched in candidates:
            route = sched.route
            if not route:  # Skip if no route
                continue

            # Build stops sequence: [origin, stops..., destination]
            stops_seq = [route.origin.lower()]
            if route.stops:
                stops_seq += [s.strip().lower() for s in route.stops.split(",") if s.strip()]
            stops_seq.append(route.destination.lower())

            # Check if source and destination are in the route in correct order
            try:
                # Find source (partial match)
                source_idx = -1
                for i, stop in enumerate(stops_seq):
                    if source in stop:
                        source_idx = i
                        break
                
                # Find destination after source
                dest_idx = -1
                for i in range(source_idx + 1, len(stops_seq)):
                    if destination in stops_seq[i]:
                        dest_idx = i
                        break
                
                if source_idx == -1 or dest_idx == -1:
                    continue
                    
            except Exception:
                continue  # Source or destination not found in route

            # Check date/day matching
            if travel_date_obj:
                # If schedule has specific date, check if it matches
                if sched.date:
                    if sched.date != travel_date_obj:
                        continue
                # If schedule has days, check if day matches
                elif sched.days and target_day_abbr:
                    if target_day_abbr not in sched.days:
                        continue
                else:
                    # No date or days specified, skip
                    continue
            elif target_day_abbr:
                # Only day filter provided (no specific date)
                if sched.days:
                    if target_day_abbr not in sched.days:
                        continue
                else:
                    # No days specified, skip
                    continue

            bus = sched.bus
            
            # Get other filter parameters
            bus_type = request.GET.get('bus_type', '')
            sleeper_type = request.GET.get('sleeper_type', '')
            is_woman_safe = request.GET.get('is_woman_safe', '') == 'on'
            
            # Bus type filters
            if bus_type:
                if bus_type == "AC" and bus.ac_type != "AC":
                    continue
                if bus_type == "Non-AC" and bus.ac_type != "Non-AC":
                    continue
            
            # Sleeper type filters
            if sleeper_type:
                if sleeper_type == "Sleeper" and not bus.is_sleeper:
                    continue
                if sleeper_type == "Seater" and bus.is_sleeper:
                    continue
            
            # Women safety filter
            if is_woman_safe:
                if not bus.driver_name:
                    continue

            avail = seats_available(sched)
            if avail <= 0:
                continue

            schedules_ctx.append(_schedule_to_context(sched))

    return render(
        request,
        "main/search_results.html",
        {
            "form": form,
            "schedules": schedules_ctx,
            "origin": source,
            "destination": destination,
            "travel_date": travel_date,
            "selected_day": day_filter,
        },
    )

def search_results(request):
    source = request.GET.get("source", "")
    destination = request.GET.get("destination", "")
    day = request.GET.get("day", "")
    bus_type = request.GET.get("bus_type", "")
    sleeper_type = request.GET.get("sleeper_type", "")
    is_woman_safe = request.GET.get("is_woman_safe", False)

    schedules = Schedule.objects.select_related("bus").all()

    # Search origin
    if source:
        schedules = schedules.filter(bus__origin__icontains=source)

    # Search destination
    if destination:
        schedules = schedules.filter(bus__destination__icontains=destination)

    # Search stops (optional)
    if source:
        schedules = schedules.filter(
            Q(bus__origin__icontains=source) |
            Q(bus__stops__icontains=source)
        )

    if destination:
        schedules = schedules.filter(
            Q(bus__destination__icontains=destination) |
            Q(bus__stops__icontains=destination)
        )

    # Filter by day
    if day:
        schedules = schedules.filter(days__icontains=day)

    # AC / Non AC
    if bus_type:
        schedules = schedules.filter(bus__ac_type=bus_type)

    # Sleeper/Seater
    if sleeper_type:
        if sleeper_type == "Sleeper":
            schedules = schedules.filter(bus__is_sleeper=True)
        elif sleeper_type == "Seater":
            schedules = schedules.filter(bus__is_sleeper=False)

    # Women safety — simple version
    if is_woman_safe:
        schedules = schedules.filter(bus__driver_name__icontains="safe")

    return render(request, "main/search_results.html", {
        "schedules": schedules
    })

@login_required(login_url="login")
def user_dashboard(request):
    """
    Shows bookings for the logged-in user and frequent routes.
    """
    bookings = request.user.bookings.select_related("schedule__route", "schedule__bus").order_by("-created_at")
    routes = [
        (b.schedule.route.origin, b.schedule.route.destination)
        for b in bookings
        if b.schedule and b.schedule.route
    ]
    freq = Counter(routes).most_common(5)
    return render(
        request,
        "main/user_dashboard.html",
        {
            "bookings": bookings,
            "frequent_routes": freq,
        },
    )


@login_required(login_url="login")
def conductor_dashboard(request):
    """
    Conductor's dashboard showing their buses and schedules.
    Requires the logged-in user to have a Conductor profile.
    """
    conductor = getattr(request.user, "conductor", None)
    if not conductor:
        return redirect("conductor_register")
    buses = conductor.buses.prefetch_related("routes", "schedules", "schedules__bookings")
    # prepare a small context for templates
    buses_ctx = []
    for b in buses:
        schedules = []
        for s in b.schedules.all():
            schedules.append(_schedule_to_context(s))
        buses_ctx.append({"bus": b, "schedules": schedules})
    return render(request, "main/conductor_dashboard.html", {"buses": buses_ctx})


@login_required(login_url="login")
def conductor_register(request):
    """
    Register the logged-in user as a Conductor.
    """
    conductor = getattr(request.user, "conductor", None)
    if conductor is not None:
        messages.info(request, "You are already registered as a conductor.")
        return redirect("register_bus")

    if request.method == "POST":
        form = ConductorForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.user = request.user
            c.save()
            messages.success(request, "Conductor profile created. You can now register your bus.")
            return redirect("register_bus")
    else:
        form = ConductorForm()
    return render(request, "main/conductor_register.html", {"form": form})


@login_required(login_url="login")
def register_bus(request):
    conductor = getattr(request.user, "conductor", None)
    if conductor is None:
        messages.info(request, "Create a conductor profile first.")
        return redirect("conductor_register")

    if request.method == "POST":
        bus_name = request.POST.get("bus_name", "").strip() or "Unnamed bus"
        registration_number = request.POST.get("bus_number", "").strip()
        
        # Check if registration number is provided
        if not registration_number:
            messages.error(request, "Registration number is required.")
            return redirect("register_bus")
        
        # Check if registration number already exists
        if Bus.objects.filter(registration_number=registration_number).exists():
            messages.error(request, f"A bus with registration number '{registration_number}' already exists.")
            return redirect("register_bus")

        total_seats = request.POST.get("total_seats") or 40
        try:
            total_seats = int(total_seats)
        except (TypeError, ValueError):
            total_seats = 40

        from_city = request.POST.get("from_city", "").strip() or "Unknown"
        to_city = request.POST.get("to_city", "").strip() or "Unknown"
        departure_time = request.POST.get("departure_time", "").strip() or "00:00"
        arrival_time = request.POST.get("arrival_time", "").strip() or "00:00"
        
        # Get days (checkboxes)
        days_selected = request.POST.getlist("days")
        days_value = ",".join(days_selected) if days_selected else ""
        
        # Get specific date (optional)
        specific_date_str = request.POST.get("specific_date", "").strip()
        specific_date = None
        if specific_date_str:
            try:
                specific_date = datetime.strptime(specific_date_str, "%Y-%m-%d").date()
            except:
                pass

        stop_times = request.POST.getlist("stop_times[]")
        stops_list = request.POST.getlist("stops[]") or []

        stops_string = ",".join([s.strip() for s in stops_list if s.strip()])

        def parse_time_str(t):
            try:
                return datetime.strptime(t, "%H:%M").time()
            except Exception:
                try:
                    return datetime.strptime(t, "%H:%M:%S").time()
                except Exception:
                    return dtime(0, 0)

        dep_t = parse_time_str(departure_time)
        arr_t = parse_time_str(arrival_time)

        try:
            with transaction.atomic():
                # Create bus with conductor
                bus = Bus.objects.create(
                    bus_name=bus_name,
                    registration_number=registration_number,
                    total_seats=total_seats,
                    conductor=conductor,
                    ac_type="AC",  # You can add this as a field in form
                    bus_type="Seater",  # You can add this as a field in form
                    is_sleeper=False,  # You can add this as a field in form
                )

                route = Route.objects.create(
                    bus=bus,
                    origin=from_city,
                    destination=to_city,
                    stops=stops_string,
                )

                # Save stops properly
                for idx, stop_name in enumerate(stops_list):
                    stop_name = stop_name.strip()
                    if not stop_name:
                        continue

                    time_str = stop_times[idx] if idx < len(stop_times) else "00:00"
                    try:
                        stop_time = datetime.strptime(time_str, "%H:%M").time()
                    except:
                        stop_time = dtime(0, 0)

                    Stop.objects.create(
                        route=route,
                        name=stop_name,
                        time=stop_time,
                        order=idx
                    )

                # Create schedule with days or specific date
                Schedule.objects.create(
                    bus=bus,
                    route=route,
                    date=specific_date,  # Will be None if not specified
                    departure_time=dep_t,
                    arrival_time=arr_t,
                    days=days_value if not specific_date else None,  # Only set days if no specific date
                )

            messages.success(request, "Bus registered successfully.")
            return redirect("conductor_dashboard")
            
        except Exception as e:
            messages.error(request, f"Error registering bus: {str(e)}")
            return redirect("register_bus")

    return render(request, "main/register_bus.html", {})

@login_required(login_url="login")
@require_POST
def start_booking(request, schedule_id):
    """
    Start booking: creates a Booking and a Payment placeholder, then redirects to payment_page.
    """
    schedule = get_object_or_404(Schedule, pk=schedule_id)
    try:
        seats_requested = int(request.POST.get("seats", 1))
    except (TypeError, ValueError):
        seats_requested = 1

    avail = seats_available(schedule)
    if seats_requested <= 0 or seats_requested > avail:
        messages.error(request, f"Only {avail} seats available.")
        # redirect back to search/bookings
        return redirect("bookings")

    # price per seat can be sent from form or defaulted
    try:
        price_per_seat = float(request.POST.get("price_per_seat", 200.0))
    except (TypeError, ValueError):
        price_per_seat = 200.0
    total_amount = seats_requested * price_per_seat

    # create booking + payment inside a transaction
    with transaction.atomic():
        booking = Booking.objects.create(
            user=request.user,
            schedule=schedule,
            seats=seats_requested,
            amount_paid=0,
            paid=False,
        )
        payment = Payment.objects.create(
            booking=booking,
            provider="razorpay",
            amount=total_amount,
            status="initiated",
        )

    return redirect("payment_page", payment_id=payment.pk)


@login_required(login_url="login")
def payment_page(request, payment_id):
    """
    Very small simulated payment page. On POST we mark payment succeeded.
    Replace with real gateway integration (Razorpay/Stripe) in production.
    """
    payment = get_object_or_404(Payment, pk=payment_id)
    if request.method == "POST":
        # Simulate the provider callback / success
        payment.status = "succeeded"
        payment.provider_payment_id = request.POST.get("provider_payment_id", "simulated")
        payment.save()

        booking = payment.booking
        booking.paid = True
        booking.amount_paid = payment.amount
        booking.save()

        messages.success(request, "Payment successful — booking confirmed.")
        return redirect("user_dashboard")

    return render(request, "main/payment_page.html", {"payment": payment})


@login_required(login_url="login")
def bookings(request):
    """Simple wrapper if you want a dedicated bookings view."""
    return render(request, "main/bookings.html")

def search(request):
    return render(request, "main/search.html")

def sectors(request):
    return render(request, "main/sectors.html")

def connected(request):
    return render(request, "main/connected.html")
def who_we_are(request):
    return render(request, "main/who_we_are.html")

def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect("index")

def get_duration(departure, arrival):
    dep = datetime.combine(datetime.today(), departure)
    arr = datetime.combine(datetime.today(), arrival)
    if arr < dep:
        arr += timedelta(days=1)    # next day arrival for overnight buses
    diff = arr - dep
    hours = diff.seconds // 3600
    mins = (diff.seconds % 3600) // 60
    return f"{hours}h {mins}m"

def calculate_price(route, bus):
    if not route:
        return 200 
    
    base = 150

    stops = [route.origin] + [s.strip() for s in route.stops.split(",") if s.strip()] + [route.destination]

    distance = len(stops) * 40

    price = base + (distance * 2)

    if bus.is_sleeper:
        price += price * 0.3

    if bus.ac_type:
        price += price * 0.2

    return int(price)
