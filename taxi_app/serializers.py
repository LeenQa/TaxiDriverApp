from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from taxi_app.models import *
from django.contrib.auth.models import Group
import re


class TaxiUserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(style={"input_type": "password"}, write_only=True)

    def validate_password(self, value):
        r = re.compile(r'(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=])(?=\S+$).{8,30}')
        if r.match(value) is None:
            raise serializers.ValidationError(
                "password must contain upper and lower case letters, numbers and special characters.")
        return value

    def validate_email(self, value):
        r = re.compile(r'^(.+)@(.+)$')
        if r.match(value) is None:
            raise serializers.ValidationError(
                "Make sure to write a valid email.")
        return value

    def validate_user_type(self, value):
        if not value == 'client' and not value == 'admin':
            raise serializers.ValidationError(
                "The value for user type can only be client, driver or admin")
            return value

    class Meta:
        model = TaxiUser
        fields = ['username',
                  'password',
                  'confirm_password',
                  'email',
                  'phone',
                  'address',
                  'user_type']
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def save(self):

        password = self.validated_data['password']
        confirm_password = self.validated_data['confirm_password']
        if password != confirm_password:
            print("passwords don't match.")
            raise serializers.ValidationError({"password": "passwords must match."})
        else:
            user = TaxiUser(
                email=self.validated_data['email'],
                username=self.validated_data['username'],
                phone=self.validated_data['phone'],
                address=self.validated_data['address'],
                user_type=self.validated_data['user_type'],
            )
            if self.validated_data['user_type'] == 'client':
                group = Group.objects.get(name='ClientGroup')
                group.user_set.add(user)
            elif self.validated_data['user_type'] == 'admin':
                group = Group.objects.get(name='AdminGroup')
                group.user_set.add(user)
            user.set_password(password)
            user.save()
            return user


class DriverSerializer(serializers.ModelSerializer):
    def validate_work_status(self, value):
        if not value == 'seeking' and not value == 'inactive' and not value == 'in transit':
            raise serializers.ValidationError(
                "The value for user type can only be seeking, inactive or in transit")
            return value

    class Meta:
        model = Driver
        fields = ['user',
                  'work_status']

    def save(self):
        driver = Driver(
            work_status=self.validated_data['work_status'],
            user=self.validated_data['user'],
        )
        group = Group.objects.get(name='DriverGroup')
        group.user_set.add(driver)

        driver.save()
        return driver


class TaxiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taxi
        fields = ['car_model',
                  'num_of_passengers',
                  'driver']


class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = ['duration',
                  'request_status',
                  'client',
                  'driver']


class WorkHoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkHours
        fields = ['start_time',
                  'end_time',
                  'hours',
                  'driver']
