from django.core.management.base import BaseCommand
from Zkteco_django.odoo.models import Device
from Zkteco_django.get_attendances import GetAttendance


class Command(BaseCommand):
	def add_arguments(self, parser):

		parser.add_argument('--id', required=True, action="store", help='Device ID')
		#parser.add_argument('--batch', required=True, action="store", help="Batch Size")

	def handle(self, *args, **options):
		id = options['id']
		GetAttendance(id)
