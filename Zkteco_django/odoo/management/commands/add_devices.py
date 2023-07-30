from django.core.management.base import BaseCommand
import sys
sys.path.append("../../..")
from Zkteco_django.zkteco_sync import DB

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('db_path', help='DataBase path')
        parser.add_argument('ip', help="IP")
        parser.add_argument('sn', help="SN")
        parser.add_argument('port', help="Port")
        parser.add_argument('password', help="Password")
        parser.add_argument('timeout', help="timeout")
        parser.add_argument('odoo_endpoint', help="Odoo_endpoint")
        parser.add_argument('comment', help="Comment")

    def handle(self, *args, **options):
        db_path = options['db_path']
        ip = options['ip']
        sn = options['sn']
        port = options['port']
        password = options['password']
        timeout = options['timeout']
        odoo_endpoint = options['odoo_endpoint']
        comment = options['comment']

        db = DB(db_path)

        db.add_devices(ip, sn, port, password, timeout, odoo_endpoint, comment)
