from django.db import models


class BusRoute(models.Model):
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    distance_km = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.source} → {self.destination}"


class Bus(models.Model):
    route = models.ForeignKey(BusRoute, on_delete=models.CASCADE, related_name='buses')
    name = models.CharField(max_length=100)
    bus_type = models.CharField(max_length=20, choices=[
        ('AC', 'AC'),
        ('Non-AC', 'Non-AC'),
    ])
    sleeper_type = models.CharField(max_length=20, choices=[
        ('Sleeper', 'Sleeper'),
        ('Seater', 'Seater'),
    ])
    seats_available = models.PositiveIntegerField()
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.name} ({self.route})"
