import argparse
import datetime

from prettytable import PrettyTable

from mixins import DB, ZKTeco


def add_devices(db_obj, ip, sn, port, password, timeout, odoo_endpoint, comment):
	db_obj.add_devices(ip, sn, port, password, timeout, odoo_endpoint, comment)


def show_devices(db_obj):
	all_devices = db_obj.get_all()
	table = PrettyTable()
	table.field_names = ["ID", "IP", "Port", "Serial Number", "Password", "Timeout", "Odoo Endpoint", "Comment", ]
	table.add_rows(all_devices)
	print(table)


def delete_device(db_obj, id):
	db_obj.delete(id)


def get_attendances(id):
	ZKTeco_boj = ZKTeco()

	device = db.get_device(id)
	ZKTeco_boj.create_connection(ip=device[1], port=device[2], password=device[4])

	try:
		attendances = ZKTeco_boj.get_attendances()
		last = db.get_last_data('attendances', 'day_time', device[0])
		if not last:
			db.add_to_table_attendance(attendances, device[0])
			print(f"{len(attendances)} attendances loaded to database from device {id}")

		else:
			l = list(filter(lambda x: x[1] > datetime.datetime.strptime(last[0][2], "%Y-%m-%d %H:%M:%S"), attendances))
			if l:
				db.add_to_table_attendance(l, device[0])
				print(f"{len(l)} attendances loaded to database from device {id}")
	except Exception as e:
		print("Process terminate : {}".format(e))


def edit_device(db_obj, id, ip, port, password, timeout, odoo_endpoint, comment):
	db_obj.edit_device(id, ip, port, password, timeout, odoo_endpoint, comment)


def upload_attendances(db_obj, id, batch):
	if id:
		db_obj.upload(id, batch)

	else:
		all_devices = db_obj.get_all()
		for device in all_devices:
			db_obj.upload(device[0], batch)


if __name__ == '__main__':
	global_parser = argparse.ArgumentParser()
	subparsers = global_parser.add_subparsers(dest="commands", help="Odoo - ZKTeco synchronization tool")

	add_device_parser = subparsers.add_parser("add-device", help="Add a device to database")
	add_device_parser.add_argument("--ip", required=True, action="store")
	add_device_parser.add_argument("--port", default=4370, type=int, action="store")
	add_device_parser.add_argument("--sn", required=True, action="store")
	add_device_parser.add_argument("--timeout", default=10, action="store")
	add_device_parser.add_argument("--password", default=0, action="store")
	add_device_parser.add_argument("--odoo-endpoint", required=False, action="store")
	add_device_parser.add_argument("--comment", required=False, action="store", help="Comment")

	show_devices_parser = subparsers.add_parser("list-devices", help="Show all devices")

	edit_device_parser = subparsers.add_parser("edit-device", help="edit a device")
	edit_device_parser.add_argument("--id", "-i", required=True, action="store")
	edit_device_parser.add_argument("--ip", required=False, action="store")
	edit_device_parser.add_argument("--port", required=False, action="store")
	edit_device_parser.add_argument("--sn", required=False, action="store")
	edit_device_parser.add_argument("--timeout", required=False, action="store")
	edit_device_parser.add_argument("--password", required=False, action="store")
	edit_device_parser.add_argument("--odoo-endpoint", required=False, action="store")
	edit_device_parser.add_argument("--comment", required=False, action="store", help="Comment")

	delete_device_parser = subparsers.add_parser("delete-device", help="Delete one device")
	delete_device_parser.add_argument("id", action="store")

	get_device_parser = subparsers.add_parser("get-attendances", help="Get attendances from specific device or all devices")
	get_device_parser.add_argument("--id", "-i", action="store")

	upload_attendances_parser = subparsers.add_parser("upload-attendances", help="Upload attendances to Odoo")
	upload_attendances_parser.add_argument("--id", "-i", required=False, action="store")
	upload_attendances_parser.add_argument("--batch", "-b", required=False, type=int, default=50, action="store")

	db = DB()

	args = global_parser.parse_args()

	if args.commands == "add-device":
		add_devices(db, args.ip, args.port, args.sn, args.password, args.timeout, args.odoo_endpoint, args.comment)

	elif args.commands == "list-devices":
		show_devices(db)

	elif args.commands == "delete-device":
		delete_device(db, args.id)

	elif args.commands == "get-attendances":
		if args.id:
			get_attendances(args.id)
		else:
			all_devices = db.get_all()
			for device in all_devices:
				get_attendances(device[0])

	elif args.commands == "edit-device":
		edit_device(db, args.id, args.ip, args.port, args.password, args.timeout, args.odoo_endpoint, args.comment)

	elif args.commands == "upload-attendances":
		upload_attendances(db, args.id, args.batch)
