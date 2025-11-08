from django.db import models

from django.db import models

class Bus(models.Model):
    bus_name = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=20, unique=True)
    fleet_number = models.CharField(max_length=20, blank=True, null=True)
    is_ac = models.BooleanField(default=False)
    is_sleeper = models.BooleanField(default=False)
    total_seats = models.PositiveIntegerField(default=40)
    driver_name = models.CharField(max_length=100, blank=True, null=True)
    driver_photo = models.ImageField(upload_to='drivers/', blank=True, null=True)
    is_women_safe = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.bus_name} ({'AC' if self.is_ac else 'Non-AC'})"


class Route(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='routes')
    origin = models.CharField(max_length=150)
    destination = models.CharField(max_length=150)
    stops = models.TextField(blank=True, help_text='Comma-separated stops')

    def __str__(self):
        return f"{self.origin} → {self.destination}"

class Schedule(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='schedules')
    route = models.ForeignKey(Route, on_delete=models.SET_NULL, null=True, blank=True)
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    days = models.CharField(max_length=100, help_text='Comma-separated days e.g. Mon,Tue,Wed')

    def __str__(self):
        return f"{self.bus} {self.departure_time} → {self.arrival_time} ({self.days})"
