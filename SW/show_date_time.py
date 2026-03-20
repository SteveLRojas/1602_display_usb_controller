import signal
import time
from datetime import datetime
import display_1602_platform as disp
import display_1602_regs as regs

def stop(signum = None, frame = None):
	print("Stopping display")
	disp.stop()
	exit()

def main():
	signal.signal(signal.SIGINT, stop)
	signal.signal(signal.SIGTERM, stop)
	
	unique_id = disp.init(0x2EBDDBAD)
	if unique_id == 0:
		print("Could not find display")
		exit()

	print(f"Device ID: {disp.get_device_id():08X}")
	print(f"Unique ID: {disp.get_unique_id():08X}")
	print(f"Num rows: {disp.num_rows}")
	print(f"Num columns: {disp.num_columns}")

	disp.write_reg(regs.R_CLEAR_DISPLAY, 0)
	disp.write_string('Lizards rule!')

	time.sleep(1.0)
	disp.write_reg(regs.R_CLEAR_DISPLAY, 0)

	while True:
		now = datetime.now()

		# Format date and time
		date_str = now.strftime("%d.%m.%y")
		time_str = now.strftime("%H:%M:%S")
		
		# disp.write_reg(regs.R_CURSOR_ROW, 0)
		# disp.write_reg(regs.R_CURSOR_COL, 0)
		# disp.write_string(date_str + ' ' + time_str)

		disp.write_reg(regs.R_CURSOR_ROW, 0)
		disp.write_reg(regs.R_CURSOR_COL, 0)
		disp.write_string(date_str)
		disp.write_reg(regs.R_CURSOR_ROW, 1)
		disp.write_reg(regs.R_CURSOR_COL, 0)
		disp.write_string(time_str)

		time.sleep(1)

if __name__ == "__main__":
	main()