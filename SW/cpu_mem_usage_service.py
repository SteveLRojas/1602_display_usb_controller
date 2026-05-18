import signal
import time
from datetime import datetime
import psutil
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

	while True:
		log.info("Connecting to display")
		unique_id = disp.init(0)
		while unique_id == 0:
			time.sleep(1.0)
			unique_id = disp.init(0)
		
		if unique_id == 0x2EBDD6AD:
			disp.write_reg(regs.R_CONTRAST, 0)

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
