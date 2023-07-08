from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.auth import get_user_model


class Ride(models.Model):
    # Each instance of Ride will have a driver and a single rider.
    # Rider and driver cannot be same

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("STARTED", "Started"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    rider = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        related_name="rides_riding",
        null=True,
        blank=True,
        default=None,
    )
    driver = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="rides_driving"
    )
    current_location = models.PointField(geography=True, default=Point(0.0, 0.0))
    pickup_location = models.PointField(geography=True, default=Point(0.0, 0.0))
    dropoff_location = models.PointField(geography=True, default=Point(0.0, 0.0))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ride from {self.pickup_location} to {self.dropoff_location}"


class RideRequest(models.Model):
    ride = models.ForeignKey(
        Ride, on_delete=models.CASCADE, related_name="ride_requests"
    )
    rider = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None,
    )
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ride requested on {self.ride.pk} by {self.rider.username}"
