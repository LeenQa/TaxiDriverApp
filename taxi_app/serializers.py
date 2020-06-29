from rest_framework import serializers
from taxi_app.models import *
import re
from datetime import datetime, timezone, timedelta


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
        user = None
        request = self.context.get("request")
        if password != confirm_password:
            raise serializers.ValidationError({"password": "passwords must match."})
        elif request and hasattr(request, "user"):
            user = request.user
            if (self.validated_data['user_type'] == 'admin' or self.validated_data[
                'user_type'] == 'driver') and not user.user_type == 'admin':
                raise serializers.ValidationError(
                    {'status': 'You do not have the permission to add this type of users'})
            else:
                validated_data.pop('confirm_password')
                user = TaxiUser.create_tac
                #user.is_valid(raise_exception=True)
                user.set_password(password)
                user.save()
                return user
        else:
            raise serializers.ValidationError({'status': 'Could not add user.'})


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
    start_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M", required=False)
    end_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M", required=False)

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
    start_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M", required=False)
    end_time = serializers.DateTimeField(format="%Y-%m-%dT%H:%M", required=False)

    class Meta:
        model = WorkHours
        fields = ['start_time',
                  'end_time',
                  'duration',
                  'driver']

    def save_session(work_hours_today, driver):
        session = work_hours_today.get(driver=driver)
        session.end_time = datetime.now(timezone.utc)
        hours = session.end_time - session.start_time
        seconds_in_day = 24 * 60 * 60
        timedelta(0, 8, 562000)
        divmod(hours.days * seconds_in_day + hours.seconds, 60)
        session.duration = hours
        session.save()
