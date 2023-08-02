from Zkteco_django.odoo.models import Device, DeviceUser, Attendance, OdooInstance
import requests


def UploadAttendance(id):
	def send_attendance_batch(instance, batch):
		response = requests.post(instance.endpoint, json=batch)
		if response.status_code == 200:
			print(f"Attendance data batch sent to Odoo instance {instance.name}")
			return True
		else:
			print(f"Failed to send attendance data batch to Odoo instance {instance.name}")
			return False

	device_id = id

	try:

		device = Device.objects.get(pk=device_id)

		unsent_users = DeviceUser.objects.filter(devices=device, is_sent=False)

		for user in unsent_users:
			batch = []

			for instance in user.instances.all():
				batch_size = instance.batch_size

				attendance_data = {
					'user_id': user.id,
					'day_time': user.day_time,
					'punch': user.punch,
					'status': user.status,
					'device_id': device.id,
					# Include any other required fields
				}
				batch.append(attendance_data)

				if len(batch) >= batch_size:
					if send_attendance_batch(instance, batch):
						DeviceUser.objects.filter(id__in=[u.id for u in unsent_users]).update(is_sent=True)
					batch = []

			if batch:
				send_attendance_batch(instance, batch)
				DeviceUser.objects.filter(id__in=[u.id for u in unsent_users]).update(is_sent=True)
	except Device.DoesNotExist:
		print(f"Device with ID {device_id} does not exist.")
