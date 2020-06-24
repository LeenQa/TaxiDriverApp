from rest_framework import permissions


# a permission to restrict the creation of a request for clients only
class CreateRequest(permissions.BasePermission):
    message = "Only client is able to make a request"

    def has_object_permission(self, request, view, obj):
        return request.user.user_type == 'client'


# a permission to restrict deleting a request for clients only
class DeleteRequest(permissions.BasePermission):
    message = "Only client is able to delete a request he made"

    def has_object_permission(self, request, view, obj):
        return request.user.user_type == 'client' and request.user == obj.user


# a permission to restrict accepting a request for drivers only
class AcceptRequest(permissions.BasePermission):
    message = "Only driver is able to accept a request"

    def has_object_permission(self, request, view, obj):
        return request.user.user_type == 'driver'


# a permission to restrict changing the status of a request for drivers only
class CompleteRequest(permissions.BasePermission):
    message = "Only driver is able to change request status"

    def has_object_permission(self, request, view, obj):
        return request.user.user_type == 'driver'


# a permission to restrict adding taxi for admin only
class AddTaxi(permissions.BasePermission):
    message = "Only admin is able to add a taxi"

    def has_object_permission(self, request, view, obj):
        return request.user.user_type == 'admin'


# a permission to restrict changing the work status for drivers only
class ChangeWorkStatus(permissions.BasePermission):
    message = "Only driver is able to change work status"

    def has_object_permission(self, request, view, obj):
        return request.user.user_type == 'driver'


# a permission to restrict viewing requests for drivers and admin only
class ViewRequests(permissions.BasePermission):
    message = "Only drivers and admin are able to view the requests"

    def has_object_permission(self, request, view, obj):
        return request.user.user_type == 'driver' or request.user.user_type == 'admin'


# a permission to restrict viewing the work hours for admin only
class ViewWorkHours(permissions.BasePermission):
    message = "Only admin is able to view the drivers' work hours"

    def has_object_permission(self, request, view, obj):
        return request.user.user_type == 'admin'
