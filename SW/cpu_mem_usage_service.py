import signal
import time
from datetime import datetime
import psutil
import configparser
import logging
import display_1602_platform as disp
import display_1602_regs as regs

logging.basicConfig(
	level=logging.INFO,
	format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

def stop(signum = None, frame = None):
	log.info("Stopping display")
	disp.stop()
	exit()

def main():
	signal.signal(signal.SIGINT, stop)
	signal.signal(signal.SIGTERM, stop)

	# Set up the configuration parser
	config = configparser.ConfigParser()
	config.read('config.ini')

	# Get the path from the [settings] section, with a fallback
	conf_unique_id = config.get('settings', 'unique_id', fallback=0)
	conf_unique_id = int(conf_unique_id, 16)
	conf_contrast = config.getint('settings', 'contrast', fallback=45)
	conf_brightness_r = config.getint('settings', 'brightness_r', fallback=127)
	conf_brightness_g = config.getint('settings', 'brightness_g', fallback=127)
	conf_brightness_b = config.getint('settings', 'brightness_b', fallback=127)

	while True:
		log.info("Connecting to display")
		unique_id = disp.init(conf_unique_id)
		while unique_id == 0:
			time.sleep(1.0)
			unique_id = disp.init(conf_unique_id)
		
		disp.write_reg(regs.R_CONTRAST, conf_contrast)
		disp.write_reg(regs.R_BRIGHTNESS_R, conf_brightness_r)
		disp.write_reg(regs.R_BRIGHTNESS_G, conf_brightness_g)
		disp.write_reg(regs.R_BRIGHTNESS_B, conf_brightness_b)

		log.info("Device ID: %08X", disp.get_device_id())
		log.info("Unique ID: %08X", disp.get_unique_id())
		log.info("Num rows: %d", disp.num_rows)
		log.info("Num columns: %d", disp.num_columns)
		log.info("Reset type: %02X", disp.read_reg(regs.R_RESET_TYP))

		disp.write_reg(regs.R_CLEAR_DISPLAY, 0)
		disp.write_string('Lizards rule!')

		time.sleep(1.0)
		disp.write_reg(regs.R_CLEAR_DISPLAY, 0)
	
		try:
			#HINT: Here we assume that none of the strings take more lines.
			num_strings = 4
			lines_per_string = 1
			if disp.num_columns < 16:
				lines_per_string = 2
			disp.bouncy_init(num_strings)

			line = 0
			while True:
				now = datetime.now()
				# Format date and time
				date_str = now.strftime("%d.%m.%y")
				time_str = now.strftime("%H:%M")
				disp.bouncy_set_string('Date: ' + date_str, 0, lines_per_string)
				disp.bouncy_set_string('Time: ' + time_str, 1, lines_per_string)

				cpu_percent = psutil.cpu_percent(interval=None)
				mem_percent = psutil.virtual_memory().percent
				disp.bouncy_set_string(f"CPU: {cpu_percent}%", 2, lines_per_string)
				disp.bouncy_set_string(f"Mem: {mem_percent}%", 3, lines_per_string)

				for row in range(disp.num_rows // lines_per_string):
					disp.bouncy_update((line + row) % num_strings, row * lines_per_string)
				line = (line + 1) % num_strings

				time.sleep(1.0)

		except Exception as e:
			log.error("Something is fishy: %s", e)
			disp.stop()
			time.sleep(10.0)
			continue

if __name__ == "__main__":
	main()
