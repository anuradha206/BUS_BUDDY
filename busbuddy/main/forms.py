from django import forms
from .models import Bus, Conductor
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


User = get_user_model()

class UserRegisterForm(UserCreationForm):
    fullname = forms.CharField(max_length=100)
    phone = forms.CharField(max_length=20)

    class Meta:
        model = User
        fields = ["fullname", "email", "phone", "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False)

        fullname = self.cleaned_data.get("fullname")
        first, *last = fullname.split(" ", 1)

        user.first_name = first
        user.last_name = last[0] if last else ""
        user.email = self.cleaned_data.get("email")

        # Use email as username
        user.username = self.cleaned_data.get("email")

        if commit:
            user.save()
        return user
class BusForm(forms.ModelForm):
    class Meta:
        model = Bus
        fields = [
            'bus_name',
            'registration_number',
            'fleet_number',
            'ac_type',           # FIXED: was is_ac
            'bus_type',          # added for consistency
            'is_sleeper',
            'total_seats',
            'driver_name',
            'driver_photo',
        ]
        widgets = {
            'bus_name': forms.TextInput(attrs={'placeholder': 'Bus name', 'class': 'input'}),
            'fleet_number': forms.TextInput(attrs={'placeholder': 'Fleet number', 'class': 'input'}),
            'registration_number': forms.TextInput(attrs={'placeholder': 'Registration number', 'class': 'input'}),
            'driver_name': forms.TextInput(attrs={'placeholder': "Driver's full name", 'class': 'input'}),
            'ac_type': forms.Select(attrs={'class': 'input'}),
            'bus_type': forms.Select(attrs={'class': 'input'}),
        }


class BusDetailsForm(forms.Form):
    DAYS_CHOICES = [
        ("Mon", "Monday"),
        ("Tue", "Tuesday"),
        ("Wed", "Wednesday"),
        ("Thu", "Thursday"),
        ("Fri", "Friday"),
        ("Sat", "Saturday"),
        ("Sun", "Sunday"),
    ]

    ac_type = forms.ChoiceField(
        choices=[('AC', 'AC'), ('Non-AC', 'Non AC')],
        widget=forms.Select(attrs={'class': 'input'})
    )

    bus_type = forms.ChoiceField(
        choices=[('Seater', 'Seater'), ('Sleeper', 'Sleeper'), ('Both', 'Both')],
        widget=forms.Select(attrs={'class': 'input'})
    )

    seats = forms.IntegerField(
        min_value=1,
        label='Number of seats',
        widget=forms.NumberInput(attrs={'class': 'input'})
    )

    origin = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'input'})
    )

    destination = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'input'})
    )

    stops = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'input'}),
        help_text='Comma-separated stops'
    )

    departure_time = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'input'})
    )

    arrival_time = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'input'})
    )

    # FIXED: Checkbox list for days
    days = forms.MultipleChoiceField(
        choices=DAYS_CHOICES,
        widget=forms.CheckboxSelectMultiple
    )


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
