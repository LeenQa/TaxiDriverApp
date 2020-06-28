from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import Taxi_Service_App
from datetime import datetime
from django.utils import timezone
class TaxiUser(AbstractUser):
    TYPE = (
        ('admin', 'admin'),
        ('client', 'client'),
        ('driver', 'driver'),
    )
    phone = models.IntegerField(null=True, blank=True)
    address = models.CharField(max_length=50, null=True, blank=True)
    user_type = models.CharField(max_length=50, choices=TYPE, default='client')
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=150, blank=True)


class Driver(models.Model):
    STATUS = (
        ('seeking', 'seeking'),
        ('inactive', 'inactive'),
        ('in transit', 'in transit')
    )
    user = models.ForeignKey(Taxi_Service_App.settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    work_status = models.CharField(max_length=50, choices=STATUS, default='inactive')


class Taxi(models.Model):
    car_model = models.CharField(max_length=250)
    num_of_passengers = models.IntegerField()
    driver = models.OneToOneField(Driver, on_delete=models.CASCADE)


class Request(models.Model):
    STATUS = (
        ('new', 'new'),
        ('accepted', 'accepted'),
        ('complete', 'complete')
    )
    request_status = models.CharField(max_length=50, choices=STATUS, default='new')
    duration = models.DurationField(null=True)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE,null=True)
    client = models.ForeignKey(Taxi_Service_App.settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)

    def __str__(self):
        return f"requested by: {self.client}"


class WorkHours(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    hours = models.DurationField()
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)


@receiver(post_save, sender=Taxi_Service_App.settings.AUTH_USER_MODEL)
def create_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
