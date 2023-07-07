from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
class CustomUser(AbstractUser):
    mobile_number = models.CharField(max_length=10, blank=True, default="")
