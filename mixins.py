import sqlite3
from zk import ZK


class DB:
	def __init__(self):
		self.connection = sqlite3.connect("ZKTeco.sqlite")
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
								password VARCHAR(50)                           NOT NULL,
								timeout  INTEGER DEFAULT 5                     NOT NULL,
								location VARCHAR(255)
							);""")
	
	def get_all(self):
		return self.cursor.execute("SELECT * From devices").fetchall()
	
	def delete(self, id):
		self.cursor.execute(f"DELETE FROM devices WHERE id='{id}';").fetchone()
		self.connection.commit()
	
	def get_device(self, id):
		return self.cursor.execute(f"SELECT * From devices WHERE id is '{id}'").fetchone()
	
	def add_devices(self, ip, port, password, timeout, location):
		self.cursor.execute("INSERT INTO devices(ip, port, password, timeout, location) VALUES (?, ?, ?, ?, ?)", (ip, port, password, timeout, location))
		self.connection.commit()
	
	def get_last_data(self, table_name, order_by_with, device_id):
		t = self.cursor.execute(f"SELECT * From {table_name} WHERE device_id is {device_id} ORDER BY {order_by_with} DESC LIMIT 1").fetchall()
		if not t:
			return False
		return t
	
	def execute(self, query, data, many=False):
		if many:
			self.cursor.executemany(query, data)
		else:
			self.cursor.execute(query, data[0])
		self.connection.commit()
	
	def add_to_table_attendance(self, data, device_id):
		q = f"INSERT INTO attendances(user_id, day_time, punch, status, device_id) VALUES (?, ?, ?, ?,{device_id})"
		self.execute(q, data, len(data) > 1)


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
			print("Process terminate : {}".format(e))
		finally:
			if self.connection:
				# re-enable device after all commands already executed
				self.connection.enable_device()
