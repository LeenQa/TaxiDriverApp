from rest_framework import permissions
from .models import *
from taxi_app.models import TaxiUser


class IsAdmin(permissions.BasePermission):
    message = "Only admin can perform this action."

    def has_permission(self, request, view):
        return request.user.user_type == 'admin'


class IsDriver(permissions.BasePermission):
    message = "Only driver can perform this action."

    def has_permission(self, request, view):
        return request.user.user_type == 'driver'


class IsClient(permissions.BasePermission):
    message = "Only client can perform this action."

    def has_permission(self, request, view):
        return request.user.user_type == 'client'


class ListRequests(permissions.BasePermission):
    message = "Only driver or admin can perform this action."

    def has_permission(self, request, view):
        return request.user.user_type == 'driver' or request.user.user_type == 'admin'


class IsLoggedUser(permissions.BasePermission):
    message = "Only retrieve/update/delete records you created"

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, TaxiUser):
            return request.user.id == obj.id
        elif isinstance(obj, Request):
            return request.user == obj.driver or request.user == obj.client
        elif isinstance(obj, Driver):
            return request.user == obj.user
