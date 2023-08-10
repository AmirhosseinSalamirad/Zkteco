from django.core.management.base import BaseCommand
from odoo.models import Device, Attendance


class Command(BaseCommand):
	def add_arguments(self, parser):

		parser.add_argument('--id', required=False, action="store", help='Device ID')
		#parser.add_argument('--batch', required=True, action="store", help="Batch Size")

	def handle(self, *args, **options):
		id = options['id']
		#batch = options['batch']

		if id:
			Attendance.objects.get_attendance(id)

		else:
			all_devices = Device.objects.all()
			for device in all_devices:
				# UploadAttendance(device.id)
				Attendance.objects.get_attendance(device.id)
