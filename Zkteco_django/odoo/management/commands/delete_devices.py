from django.core.management.base import BaseCommand
from Zkteco_django.odoo.models import Devices


class Command(BaseCommand):
	help = 'Delete an entry from the devices table in the database'

	def add_arguments(self, parser):
		parser.add_argument('id', help='Device_id')

	def handle(self, *args, **options):
		id = options['id']

		try:
			device = Devices.objects.get(pk=id)
			device.delete()
			print(f"Device with ID {id} deleted successfully.")
		except Devices.DoesNotExist:
			print(f"Device with ID {id} does not exist.")
