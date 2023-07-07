from django.contrib.gis.db import models

from accounts.models import CustomUser


class Ride(models.Model):
    # Each instance of Ride will have a driver and a single rider.

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("STARTED", "Started"),
        ("COMPLETED", "Completed"),
        ("CANCELLED", "Cancelled"),
    ]

    rider = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="rides_riding",
        null=True,
        blank=True,
    )
    driver = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="rides_driving"
    )
    current_location = models.PointField(geography=True)
    pickup_location = models.PointField(geography=True)
    dropoff_location = models.PointField(geography=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ride from {self.pickup_location} to {self.dropoff_location}"
