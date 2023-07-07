from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import RideViewSet


router = SimpleRouter()
router.register("", RideViewSet, basename="rides")

urlpatterns = router.urls
