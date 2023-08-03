from django.db import models
from django.utils import timezone


# Create your models here.
class Device(models.Model):
	ip = models.GenericIPAddressField()
	port = models.IntegerField(default=4370)
	serial_number = models.CharField(max_length=255)
	password = models.CharField(max_length=50, null=True, blank=True)
	timeout = models.IntegerField(default=15)
	comment = models.CharField(max_length=255, default="", null=True, blank=True)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"Device {self.pk} with the port {self.port}"


class OdooInstance(models.Model):
	name = models.CharField(max_length=255)
	endpoint = models.TextField()
	timeout = models.IntegerField(default=60)
	batch_size = models.IntegerField(default=50)
	ignore_ssl = models.BooleanField(default=False)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return str(self.pk)


class DeviceUser(models.Model):

	name = models.CharField(max_length=255)
	image = models.ImageField(null=True, blank=True)
	device_id = models.IntegerField()
	devices = models.ManyToManyField(Device)
	instance = models.ForeignKey(OdooInstance, models.PROTECT)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return str(self.pk)


class Attendance(models.Model):
	user_id = models.ForeignKey(DeviceUser, on_delete=models.PROTECT)
	day_time = models.DateTimeField()
	punch = models.IntegerField()
	status = models.IntegerField()
	is_sent = models.BooleanField(default=False)
	device_id = models.ForeignKey(Device, on_delete=models.PROTECT)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		punch_type = "in" if self.punch == 1 else "out"
		return f"user {self.user_id} has punched ({punch_type}) at {self.day_time}"
