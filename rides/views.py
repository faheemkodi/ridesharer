from rest_framework import viewsets
from rest_framework.exceptions import ValidationError

from .models import Ride, RideRequest
from .serializers import RideSerializer, RideRequestSerializer


class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer

    # Note: For location inputs, please use the format 'POINT(longitude latitude).
    # eg. POINT(76.267303 9.931233) represents Kochi - longitude 76.267303 and latitude 9.931233
    # Longitude first, then latitude

    def perform_create(self, serializer):
        driver = serializer.validated_data["driver"]
        rider = serializer.validated_data["rider"]

        if driver == rider:
            raise ValidationError({"error": "Driver and rider cannot be the same."})

        serializer.save()


class RideRequestViewSet(viewsets.ModelViewSet):
    queryset = RideRequest.objects.all()
    serializer_class = RideRequestSerializer

    def perform_create(self, serializer):
        serializer.save(rider=self.request.user)
