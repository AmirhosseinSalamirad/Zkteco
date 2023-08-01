from django.core.management.base import BaseCommand
from Zkteco_django.odoo.models import Devices


class Command(BaseCommand):
	help = 'Get all entries from the devices table in the database'

	def handle(self, *args, **options):
		devices = Devices.objects.all()
		for device in devices:
			self.stdout.write(f"{device.id}: {device.ip} - {device.port}")  # Decide what to do here...
