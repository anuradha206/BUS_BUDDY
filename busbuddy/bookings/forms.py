from django import forms

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
    is_woman = forms.BooleanField(
        label="I’m a woman (enable security features)",
        required=False
    )
