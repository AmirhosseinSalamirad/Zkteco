from django.contrib import admin
from . models import Attendances, Devices, DeviceUsers, OdooInstances
# Register your models here.
admin.site.register(Attendances)
admin.site.register(Devices)
admin.site.register(DeviceUsers)
admin.site.register(OdooInstances)
