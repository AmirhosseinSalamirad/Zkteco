from django.contrib import admin
from .models import Attendance, Device, DeviceUser, OdooInstance


# Register your models here.

class AttendanceInline(admin.TabularInline):  # Use `admin.StackedInline` for a stacked layout instead of tabular.
	model = Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
	save_on_top = True
	save_as = True
	list_display = ['user_id', 'day_time', 'device_id', 'punch']
	search_fields = ['user_id__id', 'day_time', 'device_id__port', 'device_id__ip']
	list_filter = ['is_sent', 'created_at', 'user_id', 'device_id', 'status', ]
	readonly_fields = ('created_at', 'updated_at')


@admin.register(DeviceUser)
class DeviceUserAdmin(admin.ModelAdmin):
	inlines = [AttendanceInline]
	save_on_top = True
	save_as = True
	list_display = ['name', 'image']
	search_fields = ['name', 'devices__ip', 'devices__port']
	list_filter = ['created_at', 'devices']


@admin.register(OdooInstance)
class OdooInstanceAdmin(admin.ModelAdmin):
	save_on_top = True
	save_as = True
	list_display = ['name', 'endpoint']
	search_fields = ['name', 'endpoint']
	list_filter = ['updated_at', 'created_at']


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
	inlines = [AttendanceInline]
	save_on_top = True
	save_as = True
	list_display = ['ip', 'port']
	search_fields = ['ip', 'port']
	list_filter = ['updated_at', 'created_at']
