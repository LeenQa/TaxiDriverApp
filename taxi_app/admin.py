from django.contrib import admin
from taxi_app.models import *


admin.site.register(TaxiUser)
admin.site.register(Driver)
admin.site.register(Request)
admin.site.register(WorkHours)
admin.site.register(Taxi)
