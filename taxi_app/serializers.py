from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from taxi_app.models import *
from django.contrib.auth.models import Group
import re
from datetime import datetime, timezone

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

    class Meta:
        model = TaxiUser
        fields = ['username',
                  'password',
                  'confirm_password',
                  'first_name',
                  'last_name',
                  'email',
                  'phone',
                  'address',
                  'user_type']
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        password = self.validated_data['password']
        confirm_password = self.validated_data['confirm_password']
        if password != confirm_password:

            raise serializers.ValidationError({"password": "passwords must match."})
        else:
            validated_data.pop('confirm_password')
            user = super(TaxiUserSerializer, self).create(validated_data)
            user.set_password(password)
            user.save()
            return user


class DriverSerializer(serializers.ModelSerializer):
    class Meta:
        model = Driver
        fields = ['user',
                  'work_status']


class TaxiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Taxi
        fields = ['car_model',
                  'num_of_passengers',
                  'driver']


class RequestSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", required=False)
    end_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", required=False)
    class Meta:
        model = Request
        fields = ['id',
                  'duration',
                  'start_time',
                  'end_time',
                  'request_status',
                  'client',
                  'driver']


class WorkHoursSerializer(serializers.ModelSerializer):
    start_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", required=True)
    end_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M:%S", required=True)

    class Meta:
        model = WorkHours
        fields = ['start_time',
                  'end_time',
                  'hours',
                  'driver']
