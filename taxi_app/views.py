from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from .permissions import *
from .serializers import *
from datetime import datetime, timezone
from rest_framework.response import Response


def get_permissions_all(self):
    permission_classes = []
    if self.action == 'create':
        permission_classes = [IsAdmin]
    elif self.action == 'list':
        permission_classes = [IsAdmin]
    elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
        permission_classes = [IsAdmin]
    elif self.action == 'destroy':
        permission_classes = [IsAdmin]
    return permission_classes


class TaxiUserViewSet(viewsets.ModelViewSet):
    queryset = TaxiUser.objects.all()
    serializer_class = TaxiUserSerializer
    authentication_classes = (TokenAuthentication,)

    def get_permissions(self):
        permission_classes = get_permissions_all(self)
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsLoggedUser]
        return [permission() for permission in permission_classes]


class RequestViewSet(viewsets.ModelViewSet):
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    authentication_classes = (TokenAuthentication,)

    def get_permissions(self):
        permission_classes = []
        if self.action == 'create':
            permission_classes = [IsClient]
        elif self.action == 'list':
            permission_classes = [ListRequests]
        elif self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsDriver]
        elif self.action == 'destroy':
            permission_classes = [IsClient, IsLoggedUser]
        return [permission() for permission in permission_classes]

    def update(self, request, *args, **kwargs):
        req = self.get_object()
        serializer = RequestSerializer(data=request.data)
        if serializer.is_valid():
            curr_status = req.request_status
            next_status = serializer.validated_data['request_status']
            if curr_status == 'new' and next_status == 'accepted':
                req.start_time = datetime.now(timezone.utc)
            elif curr_status == 'accepted' and next_status == 'complete':
                req.end_time = datetime.now(timezone.utc)
                duration = req.end_time - req.start_time
                req.duration = duration
            req.request_status = next_status
            req.driver = serializer.validated_data['driver']
            req.save()
            return Response({'status': f'request has been changed from {curr_status} to {next_status}'})

        else:
            return Response({'status': 'serializer not valid'})


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    authentication_classes = (TokenAuthentication,)

    def get_permissions(self):
        permission_classes = get_permissions_all(self)
        if self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsDriver, IsLoggedUser]
        return [permission() for permission in permission_classes]

    def put(self, request, pk=None):
        driver = self.get_object()
        serializer = DriverSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            next_status = serializer.data['work_status']
            curr_status = driver.work_status
            if curr_status == 'inactive' and next_status == 'seeking':
                    WorkHours.objects.create(start_time=datetime.now(timezone.utc), driver=driver)
            elif (curr_status == 'seeking' or curr_status == 'in transit') and next_status == 'inactive':
                work_hours_today = WorkHours.objects.filter(start_time__year=datetime.now().year,
                                                            start_time__month=datetime.now().month,
                                                            start_time__day=datetime.now().day,
                                                            driver=driver)
                DriverSerializer.save_session(work_hours_today, driver)
            driver.work_status = next_status
            driver.save()
            return Response({'status': f'session updated from {curr_status} to {next_status}'})
        else:
            return Response({'status': 'serializer not valid'})


class TaxiViewSet(viewsets.ModelViewSet):
    queryset = Taxi.objects.all()
    serializer_class = TaxiSerializer
    authentication_classes = (TokenAuthentication,)

    def get_permissions(self):
        permission_classes = get_permissions_all(self)
        return [permission() for permission in permission_classes]


class WorkHoursViewSet(viewsets.ModelViewSet):
    queryset = WorkHours.objects.all()
    serializer_class = WorkHoursSerializer
    authentication_classes = (TokenAuthentication,)

    def get_permissions(self):
        permission_classes = get_permissions_all(self)
        return [permission() for permission in permission_classes]
