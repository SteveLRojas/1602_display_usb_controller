import signal
import time
from datetime import datetime
import requests
import display_1602_platform as disp
import display_1602_regs as regs

def stop(signum = None, frame = None):
	print("Stopping display")
	disp.stop()
	exit()

def main():
	signal.signal(signal.SIGINT, stop)
	signal.signal(signal.SIGTERM, stop)

	while True:
		print("Connecting to display")
		unique_id = disp.init(0)
		while unique_id == 0:
			time.sleep(1.0)
			unique_id = disp.init(0)

		print(f"Device ID: {disp.get_device_id():08X}")
		print(f"Unique ID: {disp.get_unique_id():08X}")
		print(f"Num rows: {disp.num_rows}")
		print(f"Num columns: {disp.num_columns}")
		print(f"Reset type: {disp.read_reg(regs.R_RESET_TYP):02X}")

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

			time_count = 0
			line = 0

			while True:
				now = datetime.now()
				# Format date and time
				date_str = now.strftime("%d.%m.%y")
				time_str = now.strftime("%H:%M")
				disp.bouncy_set_string('Date: ' + date_str, 0, lines_per_string)
				disp.bouncy_set_string('Time: ' + time_str, 1, lines_per_string)

				if time_count == 0:
					data = requests.get("https://wttr.in/?format=j1").json()
					if "data" in data:
						data = data["data"]
					if "current_condition" in data:
						current = data["current_condition"][0]
						temp = current["temp_C"]
						condition = current["weatherDesc"][0]["value"]
					else:
						temp = "?"
						condition = "No data"
					#print(temp)
					#print(condition)
					condition = condition[:(disp.num_columns * lines_per_string - 1)]
					disp.bouncy_set_string(f"Temp: {temp}C", 2, lines_per_string)
					disp.bouncy_set_string(condition, 3, lines_per_string)

				for row in range(disp.num_rows // lines_per_string):
					disp.bouncy_update((line + row) % num_strings, row * lines_per_string)
				line = (line + 1) % num_strings

				time_count = (time_count + 1) % 600
				time.sleep(1.0)
		except Exception as e:
			print(f"Something is fishy: {e}")
			disp.stop()
			time.sleep(10.0)
			continue


if __name__ == "__main__":
	main()