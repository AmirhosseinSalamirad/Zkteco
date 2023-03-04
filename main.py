from mixins import DB, ZKTeco
from prettytable import PrettyTable
import datetime
import argparse


def add_devices(db_obj, ip, port, password, timeout, location):
	db_obj.add_devices(ip, port, password, timeout, location)


def show_devices(db_obj):
	all_devices = db_obj.get_all()
	table = PrettyTable()
	table.field_names = ["id", "ip", "port", "password", "timeout", "location"]
	table.add_rows(all_devices)
	print(table)


def delete_device(db_obj, id):
	db_obj.delete(id)


def get_attendances(id):
	ZKTeco_boj = ZKTeco()
	
	device = db.get_device(id)
	ZKTeco_boj.create_connection(ip=device[1], port=device[2], password=device[3])
	
	conn = None
	try:
		
		attendances = ZKTeco_boj.get_attendances()
		last = db.get_last_data('attendances', 'day_time', device[0])
		if not last:
			db.add_to_table_attendance(attendances, device[0])
		
		else:
			l = list(filter(lambda x: x[1] > datetime.datetime.strptime(last[0][2], "%Y-%m-%d %H:%M:%S"), attendances))
			if l:
				db.add_to_table_attendance(l, device[0])
	
	
	except Exception as e:
		print("Process terminate : {}".format(e))


if __name__ == '__main__':
	global_parser = argparse.ArgumentParser()
	subparsers = global_parser.add_subparsers(dest="commands", help="arithmetic operations")
	
	add_device_parser = subparsers.add_parser("add_device", help="add a device to database")
	add_device_parser.add_argument("--ip", required=True, action="store")
	add_device_parser.add_argument("--port", default=4370, type=int, action="store")
	add_device_parser.add_argument("--timeout", default=5, action="store")
	add_device_parser.add_argument("--password", default=0, action="store")
	add_device_parser.add_argument("--location", required=True, action="store", help="comment")
	
	show_devices_parser = subparsers.add_parser("show_devices", help="show all devices in bash")
	
	delete_device_parser = subparsers.add_parser("delete_device", help="delete one device")
	delete_device_parser.add_argument("--id", required=True, action="store")
	
	get_device_parser = subparsers.add_parser("get_attendances", help="get attendances which are for specific device or all devices")
	get_device_parser.add_argument("--id", action="store")
	
	db = DB()
	
	args = global_parser.parse_args()
	
	if args.commands == "add_device":
		add_devices(db, args.ip, args.port, args.password, args.timeout, args.location)
		
	elif args.commands == "show_devices":
		show_devices(db)
	
	elif args.commands == "delete_device":
		delete_device(db, args.id)
		
	elif args.commands == "get_attendances":
		if args.id:
			get_attendances(args.id)
		else:
			all_devices = db.get_all()
			for device in all_devices:
				get_attendances(device[0])