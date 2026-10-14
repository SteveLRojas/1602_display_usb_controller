import signal
import time
from datetime import datetime
import sqlite3
import configparser
import logging
import display_1602_platform as disp
import display_1602_regs as regs

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

conf_db_path = None
conf_interval = None
conf_unique_id = None
conf_contrast = None

def stop(signum = None, frame = None):
	log.info("Stopping display")
	disp.stop()
	exit()

def get_local_weather():
	"""
	Fetches the most recent entry from the local SQLite database.
	Returns a dictionary of weather data or None if an error occurs.
	"""
	try:
		connection = sqlite3.connect(conf_db_path)
		cursor = connection.cursor()
		
		# Query the most recent entry
		cursor.execute("""
			SELECT temperature, pressure, humidity 
			FROM measurements 
			ORDER BY timestamp DESC 
			LIMIT 1
		""")
		row = cursor.fetchone()
		connection.close()

		if row:
			temp, press, hum = row
			return {
				"temperature": temp,
				"pressure": press,
				"humidity": hum
			}
		else:
			log.warning("No data found in database.")
			return None
	except Exception as e:
		log.exception("Failed to fetch local weather from database: %s", e)
		return None

def main():
	global conf_db_path
	global conf_interval
	global conf_unique_id
	global conf_contrast
	
	signal.signal(signal.SIGINT, stop)
	signal.signal(signal.SIGTERM, stop)
	
	# Set up the configuration parser
	config = configparser.ConfigParser()
	config.read('config.ini')

	# Get the path from the [settings] section, with a fallback
	conf_db_path = config.get('settings', 'database_path', fallback="/home/dragomir/weather.sqlite3")
	conf_interval = config.getint('settings', 'update_interval', fallback=60)
	conf_unique_id = config.get('settings', 'unique_id', fallback=0)
	conf_unique_id = int(conf_unique_id, 16)
	conf_contrast = config.getint('settings', 'contrast', fallback=45)

	while True:
		log.info("Connecting to display")
		unique_id = disp.init(conf_unique_id)
		while unique_id == 0:
			time.sleep(1.0)
			unique_id = disp.init(conf_unique_id)
		
		disp.write_reg(regs.R_CONTRAST, conf_contrast)

		log.info("Device ID: %08X", disp.get_device_id())
		log.info("Unique ID: %08X", disp.get_unique_id())
		log.info("Num rows: %d", disp.num_rows)
		log.info("Num columns: %d", disp.num_columns)
		log.info("Reset type: %04X", disp.read_reg(regs.R_RESET_TYP))

		disp.write_reg(regs.R_CLEAR_DISPLAY, 0)
		disp.write_string('Dragomir was here!')

		time.sleep(1.0)
		disp.write_reg(regs.R_CLEAR_DISPLAY, 0)

		try:
			#HINT: Here we assume that none of the strings take more lines.
			num_strings = 5
			lines_per_string = 1
			if disp.num_columns < 16:
				lines_per_string = 2
			disp.bouncy_init(num_strings)

			time_count = 0
			line = 0

			while True:
				now = datetime.now()
				# Format date and time
				date_str = now.strftime("%d.%m.%y")
				time_str = now.strftime("%H:%M")
				disp.bouncy_set_string('Date: ' + date_str, 0, lines_per_string)
				disp.bouncy_set_string('Time: ' + time_str, 1, lines_per_string)

				# Fetch local weather every 60 seconds (1 minute)
				if time_count == 0:
					data = get_local_weather()
					if data:
						temp = data["temperature"]
						press = data["pressure"]
						hum = data["humidity"]
						
						temp_str = f"Temp: {temp:.2f}C"
						press_str = f"Pres: {press:.2f}kPa"
						hum_str = f"Hum: {hum:.2f}%"
						
						temp_str = temp_str[:(disp.num_columns * lines_per_string - 1)]
						press_str = press_str[:(disp.num_columns * lines_per_string - 1)]
						hum_str = hum_str[:(disp.num_columns * lines_per_string - 1)]
						
						disp.bouncy_set_string(temp_str, 2, lines_per_string)
						disp.bouncy_set_string(press_str, 3, lines_per_string)
						disp.bouncy_set_string(hum_str, 4, lines_per_string)
					else:
						disp.bouncy_set_string("Temp: ?", 2, lines_per_string)
						disp.bouncy_set_string("Pres: Fishy", 3, lines_per_string)
						disp.bouncy_set_string("No Data", 4, lines_per_string)

				for row in range(disp.num_rows // lines_per_string):
					disp.bouncy_update((line + row) % num_strings, row * lines_per_string)
				line = (line + 1) % num_strings

				time_count = (time_count + 1) % conf_interval
				time.sleep(1.0)

		except Exception as e:
			log.error("Something is fishy: %s", e)
			disp.stop()
			time.sleep(10.0)
			continue

if __name__ == "__main__":
	main()
