from rest_framework import serializers

from .models import Ride, RideRequest


class RideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = "__all__"


class RideRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RideRequest
        fields = "__all__"
