from django.db import models
from django.utils import timezone

# Create your models here.
class Devices(models.Model):
    ip = models.CharField(max_length=50)
    port = models.IntegerField()
    serial_number = models.CharField(max_length=255)
    password = models.CharField(max_length=50)
    timeout = models.IntegerField()
    comment = models.CharField(max_length=255)

    def __str__(self):
        return f"Device {self.pk} with the port {self.port}"

class OdooInstances(models.Model):
    name = models.CharField(max_length=255)
    endpoint = models.TextField()
    timeout = models.IntegerField()
    batch_size = models.IntegerField()
    ignore_ssl = models.BooleanField(default=False)

    def __str__(self):
        return str(self.pk)

class DeviceUsers(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField()
    device_id = models.IntegerField()
    devices = models.ManyToManyField(Devices)
    instances = models.ManyToManyField(OdooInstances)

    def __str__(self):
        return self.name


class Attendances(models.Model):
    user_id = models.ForeignKey(DeviceUsers, on_delete=models.CASCADE)
    day_time = models.DateTimeField()
    punch = models.IntegerField()
    status = models.IntegerField()
    is_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now) # What should be the default?
    device_id = models.ForeignKey(Devices, on_delete=models.CASCADE)

    def __str__(self):
        punch_type = "in" if self.punch == 1 else "out"
        return f"user {self.user_id} has punched ({punch_type}) at {self.day_time}"




