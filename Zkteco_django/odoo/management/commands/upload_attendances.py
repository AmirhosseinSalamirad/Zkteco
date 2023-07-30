from django.core.management.base import BaseCommand
import sys
sys.path.append("../../..")
from Zkteco_django.zkteco_sync import DB

class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('db_path', help='DataBase path')
        parser.add_argument('id', help="ID")
        parser.add_argument('batch', help="Batch_size")

    def handle(self, *args, **options):
        db_path = options['db_path']
        id = options['id']
        batch = options['batch']

        db = DB(db_path)

        if id:
            db.upload(id, batch)
        else:
            all_devices = db.get_all()
            for device in all_devices:
                db.upload(device[0], batch)