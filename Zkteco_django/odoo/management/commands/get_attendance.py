from django.core.management.base import BaseCommand
from odoo.models import Attendance


class Command(BaseCommand):
	def add_arguments(self, parser):

		parser.add_argument('--id', required=True, action="store", help='Device ID')
		parser.add_argument('--instance', required=True, action="store", help='Odoo Instance ID')

	def handle(self, *args, **options):
		id = options['id']
		instance = options['instance']
		Attendance.objects.get_attendance(id, instance)
