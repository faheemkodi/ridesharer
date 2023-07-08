from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import RideViewSet, RideRequestViewSet


router = SimpleRouter()

router.register("requests", RideRequestViewSet, basename="ride_requests")
router.register("rides", RideViewSet, basename="rides")

urlpatterns = router.urls
