import logging
from datetime import datetime

from odoo.models import Device, Attendance

from zk import ZK


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


def get_last_data(table_name, order_by_with, device_id):
	t = table_name.objects.filter(device_id=device_id).order_by('-' + order_by_with).first()
	if not t:
		return False
	return t


def add_to_table_attendance(data, device_id):
	attendance_objects = [
		Attendance(user_id=row[0], day_time=row[1], punch=row[2], status=row[3], is_sent=0, device_id=device_id)
		for row in data
	]

	Attendance.objects.bulk_create(attendance_objects)


def GetAttendance(id):
	pass
	ZKTeco_obj = ZKTeco()
	device = Device.objects.filter(id=id).get()
	ZKTeco_obj.create_connection(ip=device.ip, port=device.port, password=device.password)

	try:
		attendances = ZKTeco_obj.get_attendances()
		last = get_last_data('Attendance', 'day_time', id)

		if not last:
			add_to_table_attendance(attendances, id)
			logging.info(f"{len(attendances)} attendances loaded to database from device {id} ({device.serial_number})")

		else:
			l = list(filter(lambda x: x[1] > datetime.datetime.strptime(last.day_time, "%Y-%m-%d %H:%M:%S"), attendances))
			if l:
				add_to_table_attendance(l, id)
				logging.info(f"{len(l)} attendances loaded to database from device {id} ({device.serial_number})")
			else:
				logging.info(f"No new data from device {id} ({device.serial_number})")
	except Exception as e:
		logging.error("Process terminate : {}".format(e))
