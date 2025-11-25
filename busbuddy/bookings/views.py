from django.shortcuts import render
from .models import Bus
from .forms import BusSearchForm

def search_buses(request):
    form = BusSearchForm(request.GET or None)
    buses = []

    if form.is_valid():
        source = form.cleaned_data['source']
        destination = form.cleaned_data['destination']
        bus_type = form.cleaned_data['bus_type']
        sleeper_type = form.cleaned_data['sleeper_type']
        is_woman = form.cleaned_data['is_woman']

        buses = Bus.objects.filter(
            route__source__icontains=source,
            route__destination__icontains=destination,
        )

        if bus_type:
            buses = buses.filter(bus_type=bus_type)
        if sleeper_type:
            buses = buses.filter(sleeper_type=sleeper_type)

        if is_woman:
            for b in buses:
                b.safe_for_women = True

    return render(request, 'bookings/search.html', {'form': form, 'buses': buses})
