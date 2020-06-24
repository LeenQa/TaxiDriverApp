from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from taxi_app.models import *
from django.contrib.auth.models import Group


class TaxiUserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(style={"input_type": "password"}, write_only=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

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
