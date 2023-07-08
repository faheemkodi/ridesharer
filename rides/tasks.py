from random import uniform
from django.contrib.gis.geos import Point
from celery import shared_task

from .models import Ride


@shared_task
def update_ride_location(ride_id):
    try:
        ride = Ride.objects.get(id=ride_id)
        # Fetch current location
        current_location = fetch_current_location(ride)
        ride.current_location = current_location
        ride.save()

    except Ride.DoesNotExist:
        pass


def fetch_current_location(ride):
    # Mock implementation. Actual current location should be sent by client.
    current_location = ride.current_location

    # Simulate movement by generating tiny offsets
    longitude_offset = uniform(-0.001, 0.001)
    latitude_offset = uniform(-0.001, 0.001)

    # Update long. and lat.
    current_location.y += longitude_offset
    current_location.x += latitude_offset

    return current_location
