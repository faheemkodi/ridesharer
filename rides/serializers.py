from rest_framework import serializers

from .models import Ride


class RideSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (
            "id",
            "rider",
            "driver",
            "current_location",
            "pickup_location",
            "dropoff_location",
            "status",
            "created_at",
            "updated_at",
        )
        model = Ride
