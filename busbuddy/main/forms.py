from django import forms
from .models import Bus

class BusForm(forms.ModelForm):
    class Meta:
        model = Bus
        fields = ['name', 'fleet_number', 'registration_number', 'driver_name', 'driver_photo']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Bus name', 'class': 'input'}),
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