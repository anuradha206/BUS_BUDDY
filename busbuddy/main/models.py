from django.db import models
from django.contrib.auth import get_user_model


class Conductor(models.Model):
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='conductor')
    phone = models.CharField(max_length=30, blank=True)
    license_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.license_number or 'no-license'}"


class Bus(models.Model):
    bus_name = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=100, unique=True)
    fleet_number = models.CharField(max_length=50, blank=True, null=True)
    ac_type = models.CharField(max_length=20, choices=[("AC", "AC"), ("Non-AC", "Non-AC")])
    bus_type = models.CharField(max_length=20, choices=[("Seater", "Seater"), ("Sleeper", "Sleeper"), ("Both", "Both")])
    is_sleeper = models.BooleanField(default=False)
    total_seats = models.IntegerField()
    driver_name = models.CharField(max_length=100, blank=True, null=True)
    driver_photo = models.ImageField(upload_to="drivers/", null=True, blank=True)
    
    # ADD THIS FIELD - Missing in your model
    conductor = models.ForeignKey(Conductor, on_delete=models.CASCADE, related_name='buses', null=True, blank=True)
    
    # These can be removed since we have Route model
    origin = models.CharField(max_length=150, blank=True, null=True)
    destination = models.CharField(max_length=150, blank=True, null=True)
    stops = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.bus_name} ({self.registration_number})"


class Route(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='routes')
    origin = models.CharField(max_length=150)
    destination = models.CharField(max_length=150)
    stops = models.TextField(blank=True, help_text='Comma-separated stops')

    def __str__(self):
        return f"{self.origin} → {self.destination}"


class Schedule(models.Model):
    bus = models.ForeignKey(Bus, on_delete=models.CASCADE, related_name='schedules')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='schedules', null=True, blank=True)
    date = models.DateField(null=True, blank=True)  # ADD THIS for specific date schedules
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    days = models.CharField(max_length=50, null=True, blank=True)  # Make optional for date-based schedules

    def __str__(self):
        return f"{self.bus.bus_name} {self.departure_time} → {self.arrival_time} ({self.days})"

User = get_user_model()


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    schedule = models.ForeignKey('Schedule', on_delete=models.CASCADE, related_name='bookings')
    seats = models.PositiveIntegerField()
    seat_numbers = models.CharField(max_length=200, blank=True)  # CSV like "1,2,3"
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled = models.BooleanField(default=False)

    def __str__(self):
        return f"Booking #{self.pk} by {self.user} for {self.schedule}"


class Payment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    provider = models.CharField(max_length=50, blank=True)  # 'razorpay', 'stripe'
    provider_payment_id = models.CharField(max_length=200, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, default='initiated')  # initiated, succeeded, failed
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.provider} {self.status} for {self.booking}"


from django.db.models import Sum
def seats_booked_for_schedule(schedule):
    booked = schedule.bookings.filter(cancelled=False).aggregate(total=Sum('seats'))['total'] or 0
    return int(booked)

def seats_available(schedule):
    return max(0, schedule.bus.total_seats - seats_booked_for_schedule(schedule))


class Stop(models.Model):
    route = models.ForeignKey(Route, related_name="stop_list", on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    time = models.TimeField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.name} ({self.time})"