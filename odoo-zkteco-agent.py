#!/bin/env python3
import argparse
import datetime
import json
import logging
import sqlite3

import requests
from prettytable import PrettyTable
from zk import ZK

"""
For more information go to gitlab.com/scarfbank/odoo/zkteco
"""

__version__ = "1.2.0"


class DB:
	def __init__(self, db_path):
		self.connection = sqlite3.connect(db_path)
		self.cursor = self.connection.cursor()
		self._create_devices_table()
		self._create_attendances_table()

	def _create_attendances_table(self):
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS attendances
							(
								id         INTEGER PRIMARY KEY ASC AUTOINCREMENT NOT NULL,
								user_id    INTEGER                               NOT NULL,
								day_time   VARCHAR(50)                           NOT NULL,
								punch      INTEGER                               NOT NULL,
								status     INTEGER                               NOT NULL,
								is_sent    BOOLEAN DEFAULT FALSE,
								created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
								device_id  INTEGER,
								FOREIGN KEY (device_id) REFERENCES devices(id)
							);""")

	def _create_devices_table(self):
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS devices
							(
								id       INTEGER PRIMARY KEY ASC AUTOINCREMENT NOT NULL,
								ip       VARCHAR(50)                           NOT NULL,
								port     INTEGER DEFAULT 4370                  NOT NULL,
								serial_number     VARCHAR(255)                 NOT NULL,
								password VARCHAR(50)                           NOT NULL,
								timeout  INTEGER DEFAULT 5                     NOT NULL,
								odoo_endpoint  VARCHAR(255)							   ,
								comment VARCHAR(255)
							);""")

	def get_all(self):
		return self.cursor.execute("SELECT * From devices").fetchall()

	def delete(self, id):
		self.cursor.execute(f"DELETE FROM devices WHERE id = ?;", (id,)).fetchone()
		self.connection.commit()

	def get_device(self, id):
		return self.cursor.execute(f"SELECT * From devices WHERE id = ?", (id,)).fetchone()

	def add_devices(self, ip, port, sn, password, timeout, odoo_endpoint, comment):
		self.cursor.execute("INSERT INTO devices(ip, port, serial_number, password, timeout,odoo_endpoint, comment) VALUES (?, ?, ?, ?, ?, ?, ?)", (ip, port, sn, password, timeout, odoo_endpoint, comment))
		self.connection.commit()

	def get_last_data(self, table_name, order_by_with, device_id):
		t = self.cursor.execute(f"SELECT * From {table_name} WHERE device_id is {device_id} ORDER BY {order_by_with} DESC LIMIT 1").fetchall()
		if not t:
			return False
		return t

	def count_device_attendances(self, device_id):
		total = self.cursor.execute(f"SELECT count(id) FROM attendances WHERE device_id = ?", (device_id,)).fetchone()
		send = self.cursor.execute(f"SELECT count(id) FROM attendances WHERE device_id = ? AND is_sent = True;", (device_id,)).fetchone()
		not_sent = self.cursor.execute(f"SELECT count(id) FROM attendances WHERE device_id = ? AND is_sent = False;", (device_id,)).fetchone()

		return total[0], send[0], not_sent[0]

	def execute(self, query, data, many=False):
		if many:
			self.cursor.executemany(query, data)
		else:
			self.cursor.execute(query, data[0])
		self.connection.commit()

	def add_to_table_attendance(self, data, device_id):
		q = f"INSERT INTO attendances(user_id, day_time, punch, status, device_id) VALUES (?, ?, ?, ?,{device_id})"
		self.execute(q, data, len(data) > 1)

	def edit_device(self, id, ip, port, password, timeout, odoo_endpoint, comment):
		query = ""
		parameters = []
		if ip:
			query += 'ip = ?'
			parameters.append(ip)
		elif port:
			query += ' port = ?'
			parameters.append(port)
		elif password:
			query += ' password = ?'
			parameters.append(password)
		elif timeout:
			query += ' timeout = ?'
			parameters.append(timeout)
		elif odoo_endpoint:
			query += ' odoo_endpoint = ?'
			parameters.append(odoo_endpoint)
		elif comment:
			query += ' comment = ?'
			parameters.append(comment)

		parameters.append(id)
		self.cursor.execute(f"UPDATE devices SET {query} WHERE id = ?", parameters)
		self.connection.commit()

	def upload(self, id, batch):
		device = self.cursor.execute(f"SELECT * From devices WHERE id = ?", (id,)).fetchone()
		odoo_address = device[6]

		if not odoo_address:
			logging.error(f"device {device[0]} ({device[7]}) has no Odoo Address, Ignoring.")
			return

		not_sent_attendances = self.cursor.execute(f"SELECT * From attendances WHERE is_sent is FALSE AND device_id =  ?", (id,)).fetchall()

		total = len(not_sent_attendances)
		saved = 0
		missing_employee = []
		while len(not_sent_attendances):
			ready_for_upload = not_sent_attendances[:batch]
			not_sent_attendances = not_sent_attendances[batch:]

			data = {'attendances': ready_for_upload, "serial_number": device[3]}
			data = json.dumps(data)
			headers = {'content-type': 'application/json'}
			response = requests.post(odoo_address, data=data, headers=headers)
			try:
				response.raise_for_status()
			except:
				logging.error(f"{response.status_code}: {response.text}")
				continue

			response_data = response.json()

			if "error" in response_data['result']:
				logging.error(f"{response_data['result']['error']}")
				return

			if "success-list" in response_data['result'] and response_data['result']["success-list"]:
				placeholders = ','.join(['?'] * len(response_data['result']["success-list"]))
				query = f"UPDATE attendances SET is_sent = TRUE WHERE id IN ({placeholders})"
				# self.cursor.execute(query, response_data['result']["success-list"])
				saved += len(response_data['result']["success-list"])

			if "duplicate-list" in response_data['result'] and response_data['result']["duplicate-list"]:
				placeholders = ','.join(['?'] * len(response_data['result']["duplicate-list"]))
				query = f"UPDATE attendances SET is_sent = TRUE WHERE id IN ({placeholders})"
				self.cursor.execute(query, response_data['result']["duplicate-list"])
				saved += len(response_data['result']["duplicate-list"])

			if "missing-employee" in response_data['result'] and response_data['result']['missing-employee']:
				missing_employee.extend(response_data['result']['missing-employee'])

			self.connection.commit()

		logging.info(f"{saved}/{total} attendances of device {device[0]} ({device[7]}) Successfully loaded to Odoo {odoo_address}")
		logging.info(f"Set `ID on Biometric Device` for your employees with this ids (on device): {missing_employee}")


class ZKTeco:

	def __init__(self):
		self.zk = None
		self.connection = None

	def create_connection(self, ip, port, password, timeout=5):
		self.zk = ZK(ip, port=port, timeout=timeout, password=password, force_udp=False, ommit_ping=False)
		self.connection = self.zk.connect()

	def __del__(self):
		if self.connection:
			self.connection.disconnect()

	def get_attendances(self):
		try:
			self.connection.disable_device()
			attendances = self.connection.get_attendance()
			return [(a.user_id, a.timestamp, a.punch, a.status) for a in attendances]
		except Exception as e:
			logging.error("Process terminate : {}".format(e))
		finally:
			if self.connection:
				# re-enable device after all commands already executed
				self.connection.enable_device()


def add_devices(db_obj, ip, sn, port, password, timeout, odoo_endpoint, comment):
	db_obj.add_devices(ip, sn, port, password, timeout, odoo_endpoint, comment)


def show_devices(db_obj):
	all_devices = db_obj.get_all()
	final_device_data = [device + db_obj.count_device_attendances(device[0]) for device in all_devices]
	table = PrettyTable()
	table.field_names = ["ID", "IP", "Port", "Serial Number", "Password", "Timeout", "Odoo Endpoint", "Comment", "Total Records", "Uploaded", "Not Uploaded"]
	table.add_rows(final_device_data)
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
			logging.info(f"{len(attendances)} attendances loaded to database from device {id} ({device[7]})")
		else:
			l = list(filter(lambda x: x[1] > datetime.datetime.strptime(last[0][2], "%Y-%m-%d %H:%M:%S"), attendances))
			if l:
				db.add_to_table_attendance(l, device[0])
				logging.info(f"{len(l)} attendances loaded to database from device {id} ({device[7]})")
			else:
				logging.info(f"No new data from device {id} ({device[7]})")
	except Exception as e:
		logging.error("Process terminate : {}".format(e))


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
	global_parser.add_argument("-d", "--database", default="zkteco.sqlite3", type=str)
	global_parser.add_argument('-v', '--verbose', action='count', default=0, help="verbosity, add more `V` for more information")
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

	upload_attendances_parser = subparsers.add_parser("upload", help="Upload attendances to Odoo")
	upload_attendances_parser.add_argument("--id", "-i", required=False, action="store")
	upload_attendances_parser.add_argument("--batch", "-b", required=False, type=int, default=50, action="store")

	args = global_parser.parse_args()

	log_level = max(logging.WARNING - args.verbose * 10, logging.DEBUG)
	logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s:%(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

	db = DB(args.database)

	if args.commands == "add-device":
		add_devices(db, args.ip, args.port, args.sn, args.password, args.timeout, args.odoo_endpoint, args.comment)

	elif args.commands == "list-devices":
		show_devices(db)

	elif args.commands == "delete-device":
		delete_device(db, args.id)

	elif args.commands == "edit-device":
		edit_device(db, args.id, args.ip, args.port, args.password, args.timeout, args.odoo_endpoint, args.comment)

	elif args.commands == "get-attendances":
		if args.id:
			get_attendances(args.id)
		else:
			all_devices = db.get_all()
			for device in all_devices:
				get_attendances(device[0])

	elif args.commands == "upload":
		upload_attendances(db, args.id, args.batch)
