from django.db import models

class Bus(models.Model):
    name = models.CharField(max_length=150)
    fleet_number = models.CharField(max_length=50, blank=True, help_text="Internal fleet number")
    registration_number = models.CharField(max_length=50, unique=True, help_text="Plate/registration")
    driver_name = models.CharField(max_length=150)
    driver_photo = models.ImageField(upload_to='drivers/', blank=True, null=True)
    seats = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.registration_number})"

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
