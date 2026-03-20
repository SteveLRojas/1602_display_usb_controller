import signal
import time
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
			disp.bouncy_init()
			lines_used = disp.bouncy_set_string('Dragons!', 0, 0)
			print(f"lines used: {lines_used}")

			while True:
				disp.bouncy_update(0)
				time.sleep(1.0)
		except Exception as e:
			print(f"Something is fishy: {e}")
			disp.stop()
			continue


if __name__ == "__main__":
	main()