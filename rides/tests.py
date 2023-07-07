from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.test import TestCase

from .models import Ride


# Create your tests here.
class RideTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.driver = get_user_model().objects.create_user(
            username="testdriver",
            email="testdriver@email.com",
            mobile_number="9895000999",
            password="secretpassword",
        )

        cls.rider = get_user_model().objects.create_user(
            username="testrider",
            email="testrider@email.com",
            mobile_number="9895000111",
            password="secretpassword",
        )

        cls.ride = Ride.objects.create(
            rider=cls.rider,
            driver=cls.driver,
            current_location=Point(9.9340738, 76.2606304),
            pickup_location=Point(9.9340738, 76.2606304),
            dropoff_location=Point(11.2588, 75.7804),
            status="STARTED",
        )

    def test_ride_model(self):
        self.assertEqual(self.ride.rider.username, "testrider")
        self.assertEqual(self.ride.driver.username, "testdriver")
        self.assertEqual(self.ride.current_location.coords, (9.9340738, 76.2606304))
        self.assertEqual(self.ride.pickup_location.coords, (9.9340738, 76.2606304))
        self.assertEqual(self.ride.dropoff_location.coords, (11.2588, 75.7804))
        self.assertEqual(self.ride.status, "STARTED")
