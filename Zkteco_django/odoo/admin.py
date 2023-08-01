from django.contrib import admin
from .models import Attendances, Devices, DeviceUsers, OdooInstances

# Register your models here.
admin.site.register(Attendances)
admin.site.register(DeviceUsers)
admin.site.register(OdooInstances)


@admin.register(Devices)
class DeviceAdmin(admin.ModelAdmin):
	save_on_top = True
	save_as = True
	list_display = ['ip', 'port']
	search_fields = []
	list_filter = []

