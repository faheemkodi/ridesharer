from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Point
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.gis.measure import Distance
from django.contrib.gis.db.models.functions import Distance as DistanceFunction

from .models import Ride, RideRequest
from .serializers import RideSerializer, RideRequestSerializer


class RideTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()

        cls.user = get_user_model().objects.create_user(
            username="testuser",
            email="testuser@email.com",
            password="secretpassword",
        )

        cls.driver = get_user_model().objects.create_user(
            username="testdriver",
            email="testdriver@email.com",
            password="secretpassword",
        )

        cls.rider = get_user_model().objects.create_user(
            username="testrider",
            email="testrider@email.com",
            password="secretpassword",
        )

        # Kozhikode - Kochi
        cls.ride1 = Ride.objects.create(
            driver=cls.driver,
            current_location=Point(75.7804, 11.2588, srid=4326),
            pickup_location=Point(75.7804, 11.2588, srid=4326),
            dropoff_location=Point(76.2606304, 9.9340738, srid=4326),
        )

        # Kozhikode - Kochi
        cls.ride2 = Ride.objects.create(
            driver=cls.driver,
            current_location=Point(75.7804, 11.2588, srid=4326),
            pickup_location=Point(75.7804, 11.2588, srid=4326),
            dropoff_location=Point(76.2606304, 9.9340738, srid=4326),
        )

        # Kochi - Kozhikode - Rider exists
        cls.ride3 = Ride.objects.create(
            rider=cls.rider,
            driver=cls.driver,
            current_location=Point(76.2606304, 9.9340738, srid=4326),
            pickup_location=Point(76.2606304, 9.9340738, srid=4326),
            dropoff_location=Point(75.7804, 11.2588, srid=4326),
        )

        # Nearby rides within 1km radius of point in Kochi
        cls.nearby_to_ride3_1 = Ride.objects.create(
            driver=cls.driver,
            current_location=Point(76.2607, 9.9341, srid=4326),
            pickup_location=Point(76.2606304, 9.9340738, srid=4326),
            dropoff_location=Point(75.7804, 11.2588, srid=4326),
        )

        cls.nearby_to_ride3_2 = Ride.objects.create(
            driver=cls.driver,
            current_location=Point(76.2608, 9.9342, srid=4326),
            pickup_location=Point(76.2606304, 9.9340738, srid=4326),
            dropoff_location=Point(75.7804, 11.2588, srid=4326),
        )

        cls.nearby_to_ride3_3 = Ride.objects.create(
            driver=cls.driver,
            current_location=Point(76.2605, 9.9343, srid=4326),
            pickup_location=Point(76.2606304, 9.9340738, srid=4326),
            dropoff_location=Point(75.7804, 11.2588, srid=4326),
        )

    def test_ride_model(self):
        self.assertEqual(self.ride1.rider, None)
        self.assertEqual(self.ride1.driver.username, "testdriver")
        self.assertEqual(self.ride1.current_location.coords, (75.7804, 11.2588))
        self.assertEqual(self.ride1.pickup_location.coords, (75.7804, 11.2588))
        self.assertEqual(self.ride1.dropoff_location.coords, (76.2606304, 9.9340738))
        self.assertEqual(self.ride1.status, "PENDING")

    def test_get_all_rides(self):
        self.client.login(username="testuser", password="secretpassword")
        response = self.client.get("/api/v1/rides/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        rides = Ride.objects.all()
        expected_data = RideSerializer(rides, many=True).data
        self.assertEqual(len(rides), 6)
        self.assertEqual(response.data, expected_data)

    def test_get_all_rides_without_authenticating(self):
        response = self.client.get("/api/v1/rides/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_ride(self):
        self.client.login(username="testuser", password="secretpassword")
        ride_id = self.ride2.pk
        response = self.client.get(f"/api/v1/rides/{ride_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ride = Ride.objects.get(pk=response.data["id"])
        expected_data = RideSerializer(ride).data
        self.assertEqual(response.data, expected_data)

    def test_get_non_existent_ride(self):
        self.client.login(username="testuser", password="secretpassword")
        ride_id = 666
        response = self.client.get(f"/api/v1/rides/{ride_id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_ride_without_authenticating(self):
        ride_id = self.ride2.pk
        response = self.client.get(f"/api/v1/rides/{ride_id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_ride(self):
        self.client.login(username="testuser", password="secretpassword")
        ride_data = {
            "driver": self.user.pk,
            "current_location": "POINT(76.267303 9.931233)",
            "pickup_location": "POINT(76.267303 9.931233)",
            "dropoff_location": "POINT(76.267303 9.931233)",
        }
        response = self.client.post("/api/v1/rides/", data=ride_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Ride.objects.filter(pk=response.data["id"]))
        expected_data = RideSerializer(Ride.objects.get(pk=response.data["id"])).data
        self.assertIsNone(Ride.objects.get(pk=response.data["id"]).rider)
        self.assertEqual(response.data, expected_data)

    def tests_create_ride_without_driver(self):
        self.client.login(username="testuser", password="secretpassword")
        response = self.client.post("/api/v1/rides/", data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_ride_without_authenticating(self):
        ride_data = {
            "driver": self.user.pk,
        }
        response = self.client.post("/api/v1/rides/", data=ride_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_ride_as_driver(self):
        self.client.login(username="testdriver", password="secretpassword")
        ride_id = self.ride1.pk
        updated_ride_data = {
            "driver": self.driver.pk,
            "rider": self.rider.pk,
            "current_location": "POINT(50.0 90.0)",
            "pickup_location": "POINT(60.0 90.0)",
            "dropoff_location": "POINT(70.0 90.0)",
            "status": "COMPLETED",
        }
        response = self.client.put(
            f"/api/v1/rides/{ride_id}/",
            data=updated_ride_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ride1.refresh_from_db()
        self.assertEqual(self.ride1.rider, self.rider)
        expected_data = RideSerializer(self.ride1).data
        self.assertEqual(response.data, expected_data)

    def test_update_ride_as_rider(self):
        self.client.login(username="testrider", password="secretpassword")
        ride_id = self.ride3.pk
        updated_ride_data = {
            "driver": self.driver.pk,
            "rider": self.rider.pk,
            "current_location": "POINT(50.0 90.0)",
            "pickup_location": "POINT(60.0 90.0)",
            "dropoff_location": "POINT(70.0 90.0)",
            "status": "COMPLETED",
        }
        response = self.client.put(
            f"/api/v1/rides/{ride_id}/",
            data=updated_ride_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ride3.refresh_from_db()
        self.assertEqual(self.ride3.rider, self.rider)
        expected_data = RideSerializer(self.ride3).data
        self.assertEqual(response.data, expected_data)

    def test_update_ride_without_authenticating(self):
        ride_id = self.ride1.pk
        updated_ride_data = {
            "driver": self.driver.pk,
            "rider": self.rider.pk,
            "current_location": "POINT(50.0 90.0)",
            "pickup_location": "POINT(60.0 90.0)",
            "dropoff_location": "POINT(70.0 90.0)",
            "status": "COMPLETED",
        }
        response = self.client.put(
            f"/api/v1/rides/{ride_id}/",
            data=updated_ride_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_ride_with_invalid_data(self):
        self.client.login(username="testdriver", password="secretpassword")
        ride_id = self.ride1.pk
        updated_ride_data = {
            "driver": None,
            "rider": self.rider.pk,
            "current_location": "POINT(50.0 90.0)",
            "pickup_location": "POINT(60.0 90.0)",
            "dropoff_location": "POINT(70.0 90.0)",
            "status": "INVALID_STATUS",
        }
        response = self.client.put(
            f"/api/v1/rides/{ride_id}/",
            data=updated_ride_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_ride_as_unauthorized_user(self):
        self.client.login(username="testuser", password="secretpassword")
        ride_id = self.ride1.pk
        updated_ride_data = {
            "driver": self.driver.pk,
            "rider": self.rider.pk,
            "current_location": "POINT(50.0 90.0)",
            "pickup_location": "POINT(60.0 90.0)",
            "dropoff_location": "POINT(70.0 90.0)",
            "status": "COMPLETED",
        }
        response = self.client.put(
            f"/api/v1/rides/{ride_id}/",
            data=updated_ride_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_ride_as_driver(self):
        self.client.login(username="testdriver", password="secretpassword")
        ride_id = self.ride1.pk
        updated_ride_data = {
            "rider": self.rider.pk,
        }
        response = self.client.patch(
            f"/api/v1/rides/{ride_id}/",
            data=updated_ride_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ride1.refresh_from_db()
        self.assertEqual(self.ride1.rider, self.rider)
        expected_data = RideSerializer(self.ride1).data
        self.assertEqual(response.data, expected_data)

    def test_partial_update_ride_as_rider(self):
        self.client.login(username="testrider", password="secretpassword")
        ride_id = self.ride3.pk
        updated_ride_data = {
            "status": "COMPLETED",
        }
        response = self.client.patch(
            f"/api/v1/rides/{ride_id}/",
            data=updated_ride_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ride3.refresh_from_db()
        self.assertEqual(self.ride3.rider, self.rider)
        expected_data = RideSerializer(self.ride3).data
        self.assertEqual(response.data, expected_data)

    def test_partial_update_ride_without_authenticating(self):
        ride_id = self.ride1.pk
        updated_ride_data = {
            "rider": self.rider.pk,
        }
        response = self.client.patch(
            f"/api/v1/rides/{ride_id}/",
            data=updated_ride_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_ride_with_invalid_data(self):
        self.client.login(username="testdriver", password="secretpassword")
        ride_id = self.ride1.pk
        updated_ride_data = {
            "rider": self.rider.pk,
            "status": "SINGLE",
        }
        response = self.client.patch(
            f"/api/v1/rides/{ride_id}/",
            data=updated_ride_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_partial_update_ride_as_unauthorized_user(self):
        self.client.login(username="testuser", password="secretpassword")
        ride_id = self.ride1.pk
        updated_ride_data = {
            "rider": self.rider.pk,
        }
        response = self.client.patch(
            f"/api/v1/rides/{ride_id}/",
            data=updated_ride_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_ride_as_driver(self):
        self.client.login(username="testdriver", password="secretpassword")
        ride_id = self.ride3.pk
        response = self.client.delete(f"/api/v1/rides/{ride_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ride.objects.filter(pk=ride_id).exists())

    def test_delete_ride_as_rider(self):
        self.client.login(username="testrider", password="secretpassword")
        ride_id = self.ride3.pk
        response = self.client.delete(f"/api/v1/rides/{ride_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ride.objects.filter(pk=ride_id).exists())

    def test_delete_ride_without_authenticating(self):
        ride_id = self.ride1.pk
        response = self.client.delete(f"/api/v1/rides/{ride_id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_ride_as_unauthorized_user(self):
        self.client.login(username="testuser", password="secretpassword")
        ride_id = self.ride1.pk
        response = self.client.delete(f"/api/v1/rides/{ride_id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_ride_status_as_driver(self):
        self.client.login(username="testdriver", password="secretpassword")
        ride_id = self.ride3.pk
        updated_ride_data = {
            "status": "COMPLETED",
        }
        response = self.client.patch(
            f"/api/v1/rides/{ride_id}/",
            data=updated_ride_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ride3.refresh_from_db()
        self.assertEqual(self.ride3.status, updated_ride_data["status"])
        expected_data = RideSerializer(self.ride3).data
        self.assertEqual(response.data, expected_data)

    def test_update_ride_status_as_rider(self):
        self.client.login(username="testrider", password="secretpassword")
        ride_id = self.ride3.pk
        updated_ride_data = {
            "status": "STARTED",
        }
        response = self.client.patch(
            f"/api/v1/rides/{ride_id}/",
            data=updated_ride_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ride3.refresh_from_db()
        self.assertEqual(self.ride3.status, updated_ride_data["status"])
        expected_data = RideSerializer(self.ride3).data
        self.assertEqual(response.data, expected_data)

    def test_update_ride_status_with_invalid_data(self):
        self.client.login(username="testrider", password="secretpassword")
        ride_id = self.ride3.pk
        updated_ride_data = {
            "status": "AWAY",
        }
        response = self.client.patch(
            f"/api/v1/rides/{ride_id}/",
            data=updated_ride_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_ride_status_without_authenticating(self):
        ride_id = self.ride3.pk
        updated_ride_data = {
            "status": "STARTED",
        }
        response = self.client.patch(
            f"/api/v1/rides/{ride_id}/",
            data=updated_ride_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_ride_status_as_unauthorized_user(self):
        self.client.login(username="testuser", password="secretpassword")
        ride_id = self.ride3.pk
        updated_ride_data = {
            "status": "STARTED",
        }
        response = self.client.patch(
            f"/api/v1/rides/{ride_id}/",
            data=updated_ride_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_match_nearby_rides(self):
        self.client.login(username="testuser", password="secretpassword")
        user_longitude = 76.261
        user_latitude = 9.933
        destination_longitude = 75.781
        destination_latitude = 11.259
        request_data = {
            "user_longitude": user_longitude,
            "user_latitude": user_latitude,
            "destination_longitude": destination_longitude,
            "destination_latitude": destination_latitude,
        }
        response = self.client.post("/api/v1/rides/nearby/", data=request_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        nearby_rides = (
            Ride.objects.filter(
                rider=None,
                current_location__distance_lt=(
                    Point(user_longitude, user_latitude, srid=4326),
                    Distance(m=1000),
                ),
                dropoff_location__distance_lt=(
                    Point(destination_longitude, destination_latitude, srid=4326),
                    Distance(m=1000),
                ),
            )
            .annotate(
                distance=DistanceFunction(
                    "current_location",
                    Point(user_longitude, user_latitude, srid=4326),
                )
            )
            .order_by("distance")
        )
        expected_data = RideSerializer(nearby_rides, many=True).data
        self.assertEqual(len(nearby_rides), 3)
        self.assertEqual(response.data, expected_data)

    def test_match_nearby_rides_with_invalid_coordinates(self):
        self.client.login(username="testuser", password="secretpassword")
        user_longitude = "long"
        user_latitude = 9.933
        destination_longitude = 75.781
        destination_latitude = "lat"
        request_data = {
            "user_longitude": user_longitude,
            "user_latitude": user_latitude,
            "destination_longitude": destination_longitude,
            "destination_latitude": destination_latitude,
        }
        response = self.client.post("/api/v1/rides/nearby/", data=request_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_start_ride_tracking(self):
        ...

    def test_stop_ride_tracking(self):
        ...


class RideRequestTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = APIClient()

        cls.user = get_user_model().objects.create_user(
            username="testuser",
            email="testuser@email.com",
            password="secretpassword",
        )

        cls.driver = get_user_model().objects.create_user(
            username="testdriver",
            email="testdriver@email.com",
            password="secretpassword",
        )

        cls.rider = get_user_model().objects.create_user(
            username="testrider",
            email="testrider@email.com",
            password="secretpassword",
        )

        # Kozhikode - Kochi
        cls.ride1 = Ride.objects.create(
            driver=cls.driver,
            current_location=Point(75.7804, 11.2588, srid=4326),
            pickup_location=Point(75.7804, 11.2588, srid=4326),
            dropoff_location=Point(76.2606304, 9.9340738, srid=4326),
        )

        # Kozhikode - Kochi
        cls.ride2 = Ride.objects.create(
            driver=cls.driver,
            current_location=Point(75.7804, 11.2588, srid=4326),
            pickup_location=Point(75.7804, 11.2588, srid=4326),
            dropoff_location=Point(76.2606304, 9.9340738, srid=4326),
        )

        # Kochi - Kozhikode - Rider exists
        cls.ride3 = Ride.objects.create(
            rider=cls.rider,
            driver=cls.driver,
            current_location=Point(76.2606304, 9.9340738, srid=4326),
            pickup_location=Point(76.2606304, 9.9340738, srid=4326),
            dropoff_location=Point(75.7804, 11.2588, srid=4326),
        )

        cls.riderequest1 = RideRequest.objects.create(
            ride=cls.ride1,
            rider=cls.rider,
        )

        cls.riderequest2 = RideRequest.objects.create(
            ride=cls.ride2,
            rider=cls.rider,
        )

    def test_ride_request_model(self):
        self.assertEqual(self.riderequest1.ride, self.ride1)
        self.assertEqual(self.riderequest1.rider, self.rider)
        self.assertEqual(self.riderequest1.is_accepted, False)

    def test_get_all_ride_requests(self):
        self.client.login(username="testuser", password="secretpassword")
        response = self.client.get("/api/v1/requests/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ride_requests = RideRequest.objects.all()
        expected_data = RideRequestSerializer(ride_requests, many=True).data
        self.assertEqual(len(ride_requests), 2)
        self.assertEqual(response.data, expected_data)

    def test_get_all_ride_requests_without_authenticating(self):
        response = self.client.get("/api/v1/requests/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_ride_request(self):
        self.client.login(username="testrider", password="secretpassword")
        ride_request_id = self.riderequest1.pk
        response = self.client.get(f"/api/v1/requests/{ride_request_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ride_request = RideRequest.objects.get(pk=response.data["id"])
        expected_data = RideRequestSerializer(ride_request).data
        self.assertEqual(response.data, expected_data)

    def test_get_non_existent_ride_request(self):
        self.client.login(username="testrider", password="secretpassword")
        ride_request_id = 666
        response = self.client.get(f"/api/v1/requests/{ride_request_id}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_ride_request_without_authenticating(self):
        ride_request_id = 666
        response = self.client.get(f"/api/v1/requests/{ride_request_id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_ride_request(self):
        self.client.login(username="testuser", password="secretpassword")
        ride_request_data = {
            "ride": self.ride1.pk,
        }
        response = self.client.post("/api/v1/requests/", data=ride_request_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(RideRequest.objects.filter(pk=response.data["id"]))
        expected_data = RideRequestSerializer(
            RideRequest.objects.get(pk=response.data["id"])
        ).data
        self.assertEqual(
            RideRequest.objects.get(pk=response.data["id"]).is_accepted, False
        )
        self.assertEqual(response.data, expected_data)

    def tests_create_ride_request_for_ride_with_existing_rider(self):
        self.client.login(username="testuser", password="secretpassword")
        ride_request_data = {
            "ride": self.ride3.pk,
        }
        response = self.client.post("/api/v1/requests/", data=ride_request_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_ride_request_without_authenticating(self):
        ride_request_data = {
            "ride": self.ride1.pk,
        }
        response = self.client.post("/api/v1/requests/", data=ride_request_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_ride_request_as_driver(self):
        self.client.login(username="testdriver", password="secretpassword")
        ride_request_id = self.riderequest1.pk
        updated_ride_request_data = {
            "ride": self.riderequest1.ride.pk,
            "rider": self.riderequest1.rider.pk,
            "is_accepted": True,
        }
        response = self.client.put(
            f"/api/v1/requests/{ride_request_id}/",
            data=updated_ride_request_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.riderequest1.refresh_from_db()
        self.assertEqual(self.riderequest1.is_accepted, True)
        expected_data = RideRequestSerializer(self.riderequest1).data
        self.assertEqual(response.data, expected_data)

    def test_update_ride_request_as_rider(self):
        self.client.login(username="testrider", password="secretpassword")
        ride_request_id = self.riderequest1.pk
        updated_ride_request_data = {
            "ride": self.riderequest1.ride.pk,
            "rider": self.riderequest1.rider.pk,
            "is_accepted": True,
        }
        response = self.client.put(
            f"/api/v1/requests/{ride_request_id}/",
            data=updated_ride_request_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_ride_request_as_unauthorized_user(self):
        self.client.login(username="testuser", password="secretpassword")
        ride_request_id = self.riderequest1.pk
        updated_ride_request_data = {
            "ride": self.riderequest1.ride.pk,
            "rider": self.riderequest1.rider.pk,
            "is_accepted": True,
        }
        response = self.client.put(
            f"/api/v1/requests/{ride_request_id}/",
            data=updated_ride_request_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_ride_request_without_authenticating(self):
        ride_request_id = self.riderequest1.pk
        updated_ride_request_data = {
            "ride": self.riderequest1.ride.pk,
            "rider": self.riderequest1.rider.pk,
            "is_accepted": True,
        }
        response = self.client.put(
            f"/api/v1/requests/{ride_request_id}/",
            data=updated_ride_request_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_ride_request_as_driver(self):
        self.client.login(username="testdriver", password="secretpassword")
        ride_request_id = self.riderequest1.pk
        updated_ride_request_data = {
            "is_accepted": True,
        }
        response = self.client.patch(
            f"/api/v1/requests/{ride_request_id}/",
            data=updated_ride_request_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.riderequest1.refresh_from_db()
        self.assertEqual(self.riderequest1.is_accepted, True)
        expected_data = RideRequestSerializer(self.riderequest1).data
        self.assertEqual(response.data, expected_data)

    def test_partial_update_ride_request_as_rider(self):
        self.client.login(username="testrider", password="secretpassword")
        ride_request_id = self.riderequest1.pk
        updated_ride_request_data = {
            "ride": self.riderequest1.ride.pk,
            "rider": self.riderequest1.rider.pk,
            "is_accepted": True,
        }
        response = self.client.patch(
            f"/api/v1/requests/{ride_request_id}/",
            data=updated_ride_request_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_ride_request_as_unauthorized_user(self):
        self.client.login(username="testuser", password="secretpassword")
        ride_request_id = self.riderequest1.pk
        updated_ride_request_data = {
            "ride": self.riderequest1.ride.pk,
            "rider": self.riderequest1.rider.pk,
            "is_accepted": True,
        }
        response = self.client.patch(
            f"/api/v1/requests/{ride_request_id}/",
            data=updated_ride_request_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_partial_update_ride_request_without_authenticating(self):
        ride_request_id = self.riderequest1.pk
        updated_ride_request_data = {
            "ride": self.riderequest1.ride.pk,
            "rider": self.riderequest1.rider.pk,
            "is_accepted": True,
        }
        response = self.client.patch(
            f"/api/v1/requests/{ride_request_id}/",
            data=updated_ride_request_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_ride_request_as_driver(self):
        self.client.login(username="testdriver", password="secretpassword")
        ride_request_id = self.riderequest1.pk
        response = self.client.delete(f"/api/v1/requests/{ride_request_id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_ride_request_as_rider(self):
        self.client.login(username="testrider", password="secretpassword")
        ride_request_id = self.riderequest1.pk
        response = self.client.delete(f"/api/v1/requests/{ride_request_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(RideRequest.objects.filter(pk=ride_request_id).exists())

    def test_delete_ride_request_without_authenticating(self):
        ride_request_id = self.riderequest1.pk
        response = self.client.delete(f"/api/v1/requests/{ride_request_id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_ride_request_as_unauthorized_user(self):
        self.client.login(username="testuser", password="secretpassword")
        ride_request_id = self.riderequest1.pk
        response = self.client.delete(f"/api/v1/requests/{ride_request_id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_accept_ride_request_as_driver(self):
        self.client.login(username="testdriver", password="secretpassword")
        ride_request_id = self.riderequest1.pk
        response = self.client.patch(f"/api/v1/requests/{ride_request_id}/accept/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.riderequest1.refresh_from_db()
        self.assertEqual(self.riderequest1.is_accepted, True)
        expected_data = RideRequestSerializer(self.riderequest1).data
        self.assertEqual(response.data, expected_data)

    def test_accept_ride_request_as_rider(self):
        self.client.login(username="testrider", password="secretpassword")
        ride_request_id = self.riderequest1.pk
        response = self.client.patch(f"/api/v1/requests/{ride_request_id}/accept/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_accept_ride_request_as_unauthorized_user(self):
        self.client.login(username="testuser", password="secretpassword")
        ride_request_id = self.riderequest1.pk
        response = self.client.patch(f"/api/v1/requests/{ride_request_id}/accept/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_accept_ride_request_without_authenticating(self):
        ride_request_id = self.riderequest1.pk
        response = self.client.patch(f"/api/v1/requests/{ride_request_id}/accept/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
