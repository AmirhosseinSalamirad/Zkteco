import json
import logging

from odoo.models import Device, DeviceUser, Attendance, OdooInstance
import requests


def send_attendance_batch(instance, batch, id):
	data = {'attendances': batch, "serial_number": Device.objects.get(pk=id).serial_number}
	data = json.dumps(data)
	headers = {'content-type': 'application/json'}
	response = requests.post(instance.endpoint, data=data, headers=headers)
	try:
		response.raise_for_status()
	except:
		logging.error(f"device {Device.objects.get(pj=id).id} ({Device.objects.get(pk=id).serial_number}): {response.status_code}: {response.text}")


	if response.status_code == 200:
		print(f"Attendance data batch sent to Odoo instance {instance.name}")
		return True
	else:
		print(f"Failed to send attendance data batch to Odoo instance {instance.name}")
		return False

def UploadAttendance(id):
	try:

		device = Device.objects.get(pk=id)

		unsent_users = DeviceUser.objects.filter(devices__id=id, attendance__is_sent=False)
		batch = []
		for user in unsent_users:

			instance = user.instance
			batch_size = instance.batch_size
			user_unsent_attendances = Attendance.objects.filter(user_id=user.id, is_sent=False)

			for attendance in user_unsent_attendances:

				attendance_data = {
					'user_id': attendance.id,
					'day_time': attendance.day_time.isoformat(),
					'punch': attendance.punch,
					'status': attendance.status,
					'device_id': attendance.device_id_id,
					# Include any other required fields
				}
				batch.append(attendance_data)

				if len(batch) >= batch_size:
					if send_attendance_batch(instance, batch, id):
						Attendance.objects.filter(user_id__in=[u.id for u in unsent_users]).update(is_sent=True)
						# DeviceUser.objects.filter(id__in=[u.id for u in unsent_users]).update(is_sent=True)
						batch = []

		if batch:
			if send_attendance_batch(instance, batch, id):
				Attendance.objects.filter(user_id__in=[u.id for u in unsent_users]).update(is_sent=True)

	except Device.DoesNotExist:
		print(f"Device with ID {id} does not exist.")
