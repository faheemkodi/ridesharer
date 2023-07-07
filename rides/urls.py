from django.urls import path

from .views import RideList, RideDetail


urlpatterns = [
    path("<int:pk>", RideDetail.as_view(), name="ride_detail"),
    path("", RideList.as_view(), name="ride_list"),
]
