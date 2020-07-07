from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from .permissions import *
from .serializers import *
from datetime import datetime, timezone
from rest_framework.response import Response
#from django_filters.rest_framework import DjangoFilterBackend


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
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = '__all__'

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
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = '__all__'

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
        if request.user.user_type == 'driver':
            request_list = Request.objects.filter(driver=Driver.objects.get(user=request.user))
        else:
            request_list = Request.objects.all()
        serializer = self.get_serializer(request_list, many=True)
        result_set = serializer.data
        return Response(result_set, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        if not (Request.objects.filter(request_status='new', client=request.user) or Request.objects.filter(
                request_status='accepted', client=request.user)):
            req = Request.objects.create(client=request.user)
            serializer = self.get_serializer(req)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'status': f'you cannot make multiple requests at the same time'},
                            status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['put'])
    def change_status(self, request, pk=None, name='change request status', permission_classes=[IsDriver]):
        req = self.get_object()
        serializer = RequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        curr_status = req.request_status
        next_status = serializer.validated_data['request_status']
        driver = Driver.objects.get(user=request.user)
        change_status = req.change_request_status(request, curr_status, next_status, driver)
        if change_status:
            return Response({'status': f'request has been changed from {curr_status} to {next_status}'},
                            status=status.HTTP_200_OK)
        else:
            return Response({'status': f'you cant change from {curr_status} to {next_status}'}, status=status.HTTP_403_FORBIDDEN)


class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    serializer_class = DriverSerializer
    authentication_classes = (TokenAuthentication,)
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = '__all__'

    def get_permissions(self):
        permission_classes = get_permissions_all(self)
        if self.action == 'retrieve' or self.action == 'update' or self.action == 'partial_update':
            permission_classes = [IsDriver, IsLoggedUser]
        return [permission() for permission in permission_classes]

    @action(detail=True, methods=['put'])
    def change_status(self, request, pk=None, name='change driver status', permission_classes=[IsDriver, IsLoggedUser]):
        driver = self.get_object()
        serializer = DriverSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        next_status = serializer.validated_data['work_status']
        curr_status = driver.work_status
        change = driver.change_work_status(curr_status, next_status)
        if driver.user == request.user:
            if change:
                return Response({'status': f'session updated from {curr_status} to {next_status}'},
                                status=status.HTTP_200_OK)
            else:
                return Response({'status': 'you cant change to this status'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'status': 'you can only update your own work status'}, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=True, methods=['get'])
    def work_hours(self, request, pk=None, name='get work hours', permission_classes=[IsDriver, IsLoggedUser]):
        work_hours = WorkHours.objects.filter(driver=Driver.objects.get(user=request.user))
        serializer = WorkHoursSerializer(work_hours, many=True)
        result_set = serializer.data
        return Response(result_set, status=status.HTTP_200_OK)


class TaxiViewSet(viewsets.ModelViewSet):
    queryset = Taxi.objects.all()
    serializer_class = TaxiSerializer
    authentication_classes = (TokenAuthentication,)
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = '__all__'

    def get_permissions(self):
        permission_classes = get_permissions_all(self)
        return [permission() for permission in permission_classes]


class WorkHoursViewSet(viewsets.ModelViewSet):
    queryset = WorkHours.objects.all()
    serializer_class = WorkHoursSerializer
    authentication_classes = (TokenAuthentication,)
    # filter_backends = [DjangoFilterBackend]
    # filterset_fields = '__all__'

    def get_permissions(self):
        permission_classes = get_permissions_all(self)
        return [permission() for permission in permission_classes]
