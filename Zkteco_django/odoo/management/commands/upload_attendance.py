from django.core.management.base import BaseCommand
from Zkteco_django.odoo.models import Device
from Zkteco_django.upload_attendances import UploadAttendance


class Command(BaseCommand):
	def add_arguments(self, parser):

		parser.add_argument('--id', required=False, action="store", help='Device ID')
		#parser.add_argument('--batch', required=True, action="store", help="Batch Size")

	def handle(self, *args, **options):
		id = options['id']
		#batch = options['batch']

		if id:
			UploadAttendance(id)

		else:
			all_devices = Device.objects.all()
			for device in all_devices:
				UploadAttendance(device.id)
