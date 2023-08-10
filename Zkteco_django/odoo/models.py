from django.db import models
import logging
from datetime import datetime
from zk import ZK
import json
import logging
import requests


class ZKTeco:

	def __init__(self):
		self.zk = None
		self.connection = None

	def create_connection(self, ip, port, password, timeout=5):
		self.zk = ZK(ip, port=port, timeout=timeout, password=password, force_udp=False, ommit_ping=False)
		self.connection = self.zk.connect()

	def __del__(self):
		if self.connection:
			self.connection.disconnect()

	def get_attendances(self):
		try:
			self.connection.disable_device()
			attendances = self.connection.get_attendance()
			return [(a.user_id, a.timestamp, a.punch, a.status) for a in attendances]
		except Exception as e:
			logging.error("Process terminate : {}".format(e))
		finally:
			if self.connection:
				# re-enable device after all commands already executed
				self.connection.enable_device()


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
	name = models.CharField(max_length=255, null=True)
	image = models.ImageField(null=True, blank=True)
	device_id = models.IntegerField(null=True, blank=True)
	devices = models.ManyToManyField(Device)
	instance = models.ForeignKey(OdooInstance, models.PROTECT)

	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return str(self.pk)


class AttendanceManager(models.Manager):

	def get_attendance(self, device_id, instance_id):
		ZKTeco_obj = ZKTeco()
		device = Device.objects.filter(id=device_id).get()
		ZKTeco_obj.create_connection(ip=device.ip, port=device.port, password=device.password)

		try:
			attendances = ZKTeco_obj.get_attendances()
			last = self.get_last_data(device_id, 'day_time')

			if not last:
				self.add_to_table_attendance(attendances, device_id, instance_id)
				logging.info(f"{len(attendances)} attendances loaded to database from device {device_id} ({device.serial_number})")
			else:
				last_datetime = last.day_time.strftime("%Y-%m-%d %H:%M:%S")
				l = list(filter(lambda x: x[1] > datetime.strptime(last_datetime, "%Y-%m-%d %H:%M:%S"), attendances))
				if l:
					self.add_to_table_attendance(l, device_id, instance_id)
					logging.info(f"{len(l)} attendances loaded to database from device {device_id} ({device.serial_number})")
				else:
					logging.info(f"No new data from device {device_id} ({device.serial_number})")
		except Exception as e:
			logging.error("Process terminated: {}".format(e))

	def get_last_data(self, device_id, order_by_with):
		return self.filter(device_id=device_id).order_by('-' + order_by_with).first()

	def add_to_table_attendance(self, data, device_id, instance_id):
		attendance_objects = []
		odoo_instance = OdooInstance.objects.get(pk=instance_id)

		for row in data:
			user_id = row[0]
			device = Device.objects.get(pk=device_id)
			try:
				device_user = DeviceUser.objects.get(devices__in=[device], device_id=user_id, instance_id=odoo_instance)
			except DeviceUser.DoesNotExist:
				device_user = DeviceUser.objects.create(device_id=user_id, instance=odoo_instance)
				device_user.devices.set([device])

			attendance_objects.append(
				self.model(user_id=device_user, day_time=row[1], punch=row[2], status=row[3], is_sent=False, device_id=device)
			)
		self.bulk_create(attendance_objects)

	def upload_attendance(self, device_id):
		try:
			device = Device.objects.get(pk=device_id)
			unsent_users = DeviceUser.objects.filter(devices__in=[device], attendance__is_sent=False)
			if unsent_users:
				batch = []
				for user in unsent_users:
					instance = user.instance
					batch_size = instance.batch_size
					user_unsent_attendances = self.filter(user_id=user, is_sent=False)

					for attendance in user_unsent_attendances:
						attendance_data = (
							attendance.id,
							user.device_id,
							attendance.day_time.strftime('%Y-%m-%d %H:%M:%S'),
							attendance.punch,
							attendance.status,
							attendance.is_sent,
							attendance.created_at.strftime('%Y-%m-%d %H:%M:%S'),
							attendance.device_id_id,
						)
						batch.append(attendance_data)

						if len(batch) >= batch_size:
							if self.send_attendance_batch(instance, batch, device_id):
								self.filter(user_id__in=[u.id for u in unsent_users]).update(is_sent=True)
								batch = []

				if batch:
					if self.send_attendance_batch(instance, batch, device_id):
						self.filter(user_id__in=[u.id for u in unsent_users]).update(is_sent=True)

			else:
				print(f"There are no new attendances on Device with ID {device_id}.")
		except Device.DoesNotExist:
			print(f"Device with ID {device_id} does not exist.")

	def send_attendance_batch(self, instance, batch, device_id):
		data = {'attendances': batch, "serial_number": Device.objects.get(pk=device_id).serial_number}
		data = json.dumps(data)
		headers = {'content-type': 'application/json'}
		response = requests.post(instance.endpoint, data=data, headers=headers)

		try:
			response.raise_for_status()
		except:
			logging.error(f"device {Device.objects.get(pk=device_id).id} ({Device.objects.get(pk=device_id).serial_number}): {response.status_code}: {response.text}")

		if response.status_code == 200:
			print(f"Attendance data batch sent to Odoo instance {instance.name}")
			return True
		else:
			print(f"Failed to send attendance data batch to Odoo instance {instance.name}")
			return False


class Attendance(models.Model):
	user_id = models.ForeignKey(DeviceUser, on_delete=models.PROTECT)
	day_time = models.DateTimeField()
	punch = models.IntegerField()
	status = models.IntegerField()
	is_sent = models.BooleanField(default=False)
	device_id = models.ForeignKey(Device, on_delete=models.PROTECT)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	objects = AttendanceManager()

	def __str__(self):
		punch_type = "in" if self.punch == 1 else "out"
		return f"user {self.user_id} has punched ({punch_type}) at {self.day_time}"
