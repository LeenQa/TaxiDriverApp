from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from django.urls import include
from . import views
from rest_framework.authtoken.views import obtain_auth_token

app_name = 'taxi_app'

router = DefaultRouter()
router.register(r'drivers', views.DriverViewSet)
router.register(r'taxi-users', views.TaxiUserViewSet)
router.register(r'taxis', views.TaxiViewSet)
router.register(r'requests', views.RequestUserViewSet)
router.register(r'work-hours', views.WorkHoursViewSet)


urlpatterns = [
    url(r'login/$', obtain_auth_token, name="login"),
    url('', include(router.urls)),
]
