from django.contrib import admin
from taxi_app.models import *
#from django.contrib.auth import get_user_model
#TaxiUser = get_user_model()

admin.site.register(TaxiUser)
admin.site.register(Driver)
admin.site.register(Request)
admin.site.register(WorkHours)
admin.site.register(Taxi)
