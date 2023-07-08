from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.gis.measure import Distance
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance as DistanceFunction

from .models import Ride, RideRequest
from .permissions import (
    IsDriverOrRiderElseReadOnly,
    UpdateIfDriverDeleteIfRiderElseCreate,
)
from .serializers import RideSerializer, RideRequestSerializer
from .utils import start_ride_tracking, stop_ride_tracking


class RideViewSet(viewsets.ModelViewSet):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    permission_classes = (IsDriverOrRiderElseReadOnly,)

    # Note: For location inputs to the API, please use the format 'POINT(longitude latitude)'.
    # eg. POINT(76.267303 9.931233) represents Kochi - longitude 76.267303 and latitude 9.931233

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)

        if response.status_code == status.HTTP_201_CREATED:
            ride = response.data
            ride_id = ride.get("id")

            # Start ride tracking when ride is created
            start_ride_tracking(ride_id)

        return response

    @action(detail=True, methods=["patch"])
    def status(self, request, pk=None):
        ride = self.get_object()

        if request.user != ride.driver and request.user != ride.rider:
            return Response(
                {
                    "error": "Only a driver or rider associated with a ride can change it's status."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        status_choice = request.data.get("status")

        if status_choice not in dict(Ride.STATUS_CHOICES):
            return Response(
                {
                    "error": "Invalid status choice. Accepted values = ['PENDING', 'STARTED', 'COMPLETED', 'CANCELLED']"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Stop ride tracking when status is completed or cancelled
        if status_choice == "COMPLETED" or status_choice == "CANCELLED":
            stop_ride_tracking(ride.pk)

        ride.status = status_choice
        ride.save()

        serializer = self.get_serializer(ride)
        return Response(serializer.data)

    @action(detail=False, methods=["post"])
    def nearby(self, request, pk=None):
        coordinates = {
            "user_longitude": request.data.get("user_longitude"),
            "user_latitude": request.data.get("user_latitude"),
            "destination_longitude": request.data.get("destination_longitude"),
            "destination_latitude": request.data.get("destination_latitude"),
        }
        for key, value in coordinates.items():
            try:
                coordinates[key] = float(value)
            except ValueError:
                return Response(
                    {"error": "Invalid coordinate data"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        user_location = Point(
            coordinates["user_longitude"],
            coordinates["user_latitude"],
            srid=4326,
        )
        destination_location = Point(
            coordinates["destination_longitude"],
            coordinates["destination_latitude"],
            srid=4326,
        )

        nearby_rides = (
            Ride.objects.filter(
                rider=None,
                current_location__distance_lt=(user_location, Distance(m=1000)),
                dropoff_location__distance_lt=(destination_location, Distance(m=1000)),
            )
            .annotate(distance=DistanceFunction("current_location", user_location))
            .order_by("distance")
        )

        serializer = self.get_serializer(nearby_rides, many=True)
        return Response(serializer.data)


class RideRequestViewSet(viewsets.ModelViewSet):
    queryset = RideRequest.objects.all()
    serializer_class = RideRequestSerializer
    permission_classes = (UpdateIfDriverDeleteIfRiderElseCreate,)

    def create(self, request, *args, **kwargs):
        ride_id = request.data.get("ride")
        ride = Ride.objects.filter(pk=ride_id, rider=None).first()
        if not ride:
            return Response(
                {"error": "Ride does not exist or already has a rider assigned."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ride_request = RideRequest.objects.create(ride=ride, rider=request.user)
        serializer = self.get_serializer(ride_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["patch"])
    def accept(self, request, pk=None):
        ride_request = self.get_object()

        if request.user != ride_request.ride.driver:
            return Response(
                {"error": "Only the driver of the Ride can accept the RideRequest"},
                status=status.HTTP_403_FORBIDDEN,
            )

        ride_request.is_accepted = True
        ride_request.save()
        ride_request.ride.rider = ride_request.rider
        ride_request.ride.save()

        serializer = self.get_serializer(ride_request)
        return Response(serializer.data)
