from django import forms
from .models import Bus
from .models import Conductor

class BusForm(forms.ModelForm):
    class Meta:
        model = Bus
        fields = [
            'bus_name', 'registration_number', 'fleet_number',
            'is_ac', 'is_sleeper', 'total_seats',
            'driver_name', 'driver_photo',
        ]
        widgets = {
            'bus_name': forms.TextInput(attrs={'placeholder': 'Bus name', 'class': 'input'}),
            'fleet_number': forms.TextInput(attrs={'placeholder': 'Fleet number', 'class': 'input'}),
            'registration_number': forms.TextInput(attrs={'placeholder': 'Registration number', 'class': 'input'}),
            'driver_name': forms.TextInput(attrs={'placeholder': "Driver's full name", 'class': 'input'}),
        }

class BusDetailsForm(forms.Form):
    seats = forms.IntegerField(min_value=1, label='Number of seats', widget=forms.NumberInput(attrs={'class':'input'}))
    origin = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class':'input'}))
    destination = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class':'input'}))
    stops = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows':2, 'class':'input'}), help_text='Comma-separated stops')
    departure_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M', attrs={'type':'time', 'class':'input'}))
    arrival_time = forms.TimeField(widget=forms.TimeInput(format='%H:%M', attrs={'type':'time', 'class':'input'}))
    days = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class':'input'}), help_text='Comma-separated days e.g. Mon,Tue')

# BusSearchForm migrated from bookings/forms.py — used by main.views.search_buses
class BusSearchForm(forms.Form):
    source = forms.CharField(label="From", max_length=100)
    destination = forms.CharField(label="To", max_length=100)
    bus_type = forms.ChoiceField(
        choices=[('', 'Any'), ('AC', 'AC'), ('Non-AC', 'Non-AC')],
        required=False
    )
    sleeper_type = forms.ChoiceField(
        choices=[('', 'Any'), ('Sleeper', 'Sleeper'), ('Seater', 'Seater')],
        required=False
    )
    is_woman_safe = forms.BooleanField(
        label="I’m a woman (enable security features)",
        required=False
    )


class ConductorForm(forms.ModelForm):
    class Meta:
        model = Conductor
        fields = ['phone', 'license_number']
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': 'Phone', 'class': 'input'}),
            'license_number': forms.TextInput(attrs={'placeholder': 'License number', 'class': 'input'}),
        }