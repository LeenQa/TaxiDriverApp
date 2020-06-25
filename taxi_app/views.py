from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions

from . import customviewset
from .permissions import *
from .serializers import *
#from django.contrib.auth import get_user_model
#TaxiUser = get_user_model()

class TaxiUserViewSet(viewsets.ModelViewSet):
    queryset = TaxiUser.objects.all()
    serializer_class = TaxiUserSerializer
    authentication_classes = (TokenAuthentication,)

    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'list':
            permission_classes = [IsAdmin]
        elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsLoggedUser]
        elif self.action == 'destroy':
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]


class RequestViewSet(customviewset.CustomViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    authentication_classes = (TokenAuthentication,)

    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [IsClient]
        elif self.action == 'list':
            permission_classes = [IsDriver]
        elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsDriver]
        elif self.action == 'destroy':
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    authentication_classes = (TokenAuthentication,)

    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [IsAdmin]
        elif self.action == 'list':
            permission_classes = [IsAdmin]
        elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAdmin]
        elif self.action == 'destroy':
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]


class TaxiViewSet(viewsets.ModelViewSet):
    queryset = Taxi.objects.all()
    serializer_class = TaxiSerializer
    authentication_classes = (TokenAuthentication,)

    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [IsAdmin]
        elif self.action == 'list':
            permission_classes = [IsAdmin]
        elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAdmin]
        elif self.action == 'destroy':
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]


class WorkHoursViewSet(viewsets.ModelViewSet):
    queryset = WorkHours.objects.all()
    serializer_class = WorkHoursSerializer
    authentication_classes = (TokenAuthentication,)

    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [IsAdmin]
        elif self.action == 'list':
            permission_classes = [IsAdmin]
        elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsAdmin]
        elif self.action == 'destroy':
            permission_classes = [IsAdmin]
        return [permission() for permission in permission_classes]
