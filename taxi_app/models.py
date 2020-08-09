from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import Taxi_Service_App
from datetime import datetime, timezone


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

    @staticmethod
    def create_taxi_user(self, **validated_data):
        user = TaxiUser.objects.create(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class Driver(models.Model):
    STATUS = (
        ('seeking', 'seeking'),
        ('inactive', 'inactive'),
        ('in transit', 'in transit')
    )
    user = models.ForeignKey(Taxi_Service_App.settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    work_status = models.CharField(max_length=50, choices=STATUS, default='inactive')

    # def __str__(self):
    #     return f"name: {self.user.username} | status: {self.work_status}"

    def create_driver(user):
        driver = Driver()
        driver.user = user
        driver.work_status = 'inactive'
        driver.save()

    def change_status(self, next_status):
        self.work_status = next_status
        self.save()

    def change_work_status(self, curr_status, next_status):
        change = False
        if curr_status == 'inactive':
            if next_status == 'seeking':
                WorkHours.objects.create(start_time=datetime.now(timezone.utc), driver=self)
                change = True
        elif curr_status == 'seeking':
            if next_status == 'inactive':
                work_hours_today = WorkHours.objects.filter(start_time__year=datetime.now().year,
                                                            start_time__month=datetime.now().month,
                                                            start_time__day=datetime.now().day,
                                                            driver=self, end_time=None)
                session = work_hours_today.get(driver=self)
                end_session(session)
                change = True
        if change:
            self.user = self.user
            self.change_status(next_status)
        return change


class Taxi(models.Model):
    car_model = models.CharField(max_length=250)
    num_of_passengers = models.IntegerField()
    driver = models.OneToOneField(Driver, on_delete=models.CASCADE)

    def __str__(self):
        return f"taxi {self.id} | driver: {self.driver}"


class Request(models.Model):
    STATUS = (
        ('new', 'new'),
        ('accepted', 'accepted'),
        ('complete', 'complete')
    )
    request_status = models.CharField(max_length=50, choices=STATUS, default='new')
    duration = models.IntegerField(null=True)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, null=True)
    client = models.ForeignKey(Taxi_Service_App.settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)

    def __str__(self):
        return f"requested by: {self.client} | status: {self.request_status} | duration: {self.duration} minutes"

    def change_status(self, next_status):
        self.request_status = next_status
        self.save()

    def change_request_status(self, request, curr_status, next_status, driver):
        change_status = False
        if curr_status == 'new' and next_status == 'accepted':
            if driver.work_status == 'seeking':
                self.start_time = datetime.now(timezone.utc)
                driver.change_status(next_status='in transit')
                change_status = True
        elif curr_status == 'accepted' and next_status == 'complete':
            if self.driver == driver:
                end_session(self)
                change_status = True
            driver.change_status(next_status='seeking')
        if change_status:
            self.request_status = next_status
            self.client = self.client
            self.driver = driver
            self.save()
        return change_status


class WorkHours(models.Model):
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    duration = models.IntegerField(null=True)
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)

    def __str__(self):
        return f"driver: {self.driver} | start time: {self.start_time} | end time: {self.end_time} | duration: {self.duration}"


@receiver(post_save, sender=Taxi_Service_App.settings.AUTH_USER_MODEL)
def create_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


def end_session(obj):
    obj.end_time = datetime.now(timezone.utc)
    hours = obj.end_time - obj.start_time
    hours = hours.total_seconds()
    obj.duration = hours/60
    obj.save()
