from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from . import customviewset
from .serializers import *


class TaxiUserViewSet(viewsets.ModelViewSet):
    queryset = TaxiUser.objects.all()
    serializer_class = TaxiUserSerializer
    authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)


class RequestViewSet(customviewset.CustomViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)


class TaxiViewSet(viewsets.ModelViewSet):
    queryset = Taxi.objects.all()
    serializer_class = TaxiSerializer
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)


class WorkHoursViewSet(viewsets.ModelViewSet):
    queryset = WorkHours.objects.all()
    serializer_class = WorkHoursSerializer
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
