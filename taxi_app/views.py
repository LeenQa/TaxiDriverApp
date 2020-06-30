from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
import requests
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

    def list(self, request, pk=None):
        request_list = Request.objects.filter(request_status='new')
        serializer = self.get_serializer(request_list, many=True)
        result_set = serializer.data
        return Response(result_set)

    @action(detail=True, methods=['put'])
    def change_status(self, request, pk=None, name='change request status', permission_classes=[IsDriver]):
        req = self.get_object()
        serializer = RequestSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            curr_status = req.request_status
            next_status = serializer.validated_data['request_status']
            change_status = False
            if curr_status == 'new' and next_status == 'accepted':
                req.start_time = datetime.now(timezone.utc)
                r = requests.put(f'http://127.0.0.1:8000/taxiapp/drivers/{req.driver.id}/change_status/',
                                 data={'work_status': 'in transit'})
                change_status = True
            elif curr_status == 'accepted' and next_status == 'complete':
                req.end_time = datetime.now(timezone.utc)
                duration = req.end_time - req.start_time
                duration = duration.total_seconds()
                req.duration = duration / 60
                change_status = True
                r = requests.put(f'http://127.0.0.1:8000/taxiapp/drivers/{req.driver.id}/change_status/',
                                 data={'work_status': 'seeking'})
            if change_status:
                req.request_status = next_status
                req.client = req.client
                req.driver = Driver.objects.get(user=request.user)
                req.save()
                return Response({'status': f'request has been changed from {curr_status} to {next_status}'})
            else:
                return Response({'status': f'you cant change to this status'})


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    authentication_classes = (TokenAuthentication,)

    def get_permissions(self):
        permission_classes = get_permissions_all(self)
        if self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsDriver, IsLoggedUser]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['put'])
    def change_status(self, request, pk=None, name='change driver status', permission_classes=[IsDriver, IsLoggedUser]):
        driver = self.get_object()
        serializer = DriverSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            next_status = serializer.data['work_status']
            curr_status = driver.work_status
            change = False
            if curr_status == 'inactive':
                if next_status == 'seeking':
                    WorkHours.objects.create(start_time=datetime.now(timezone.utc), driver=driver)
                    change = True
            elif curr_status == 'seeking':
                if next_status == 'inactive':
                    work_hours_today = WorkHours.objects.filter(start_time__year=datetime.now().year,
                                                                start_time__month=datetime.now().month,
                                                                start_time__day=datetime.now().day,
                                                                driver=driver, end_time=None)
                    WorkHoursSerializer.save_session(work_hours_today, driver)
                    change = True
                elif next_status == 'in transit':
                    change = True
            elif curr_status == 'in transit':
                if next_status == 'seeking':
                    change = True
            if change:
                driver.user = driver.user
                driver.work_status = next_status
                driver.save()
                return Response({'status': f'session updated from {curr_status} to {next_status}'})
            else:
                return Response({'status': f'you cant change to this status'})

    @action(detail=True, methods=['get'])
    def work_hours(self, request, pk=None, name='get work hours', permission_classes=[IsDriver, IsLoggedUser]):
        work_hours = WorkHours.objects.filter(driver=Driver.objects.get(user=request.user))
        serializer = WorkHoursSerializer(work_hours, many=True)
        result_set = serializer.data
        return Response(result_set)

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
