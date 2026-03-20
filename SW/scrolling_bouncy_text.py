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
	
	unique_id = disp.init(0)
	if unique_id == 0:
		print("Could not find display")
		exit()

	print(f"Device ID: {disp.get_device_id():08X}")
	print(f"Unique ID: {disp.get_unique_id():08X}")
	print(f"Num rows: {disp.num_rows}")
	print(f"Num columns: {disp.num_columns}")
	print(f"Reset type: {disp.read_reg(regs.R_RESET_TYP):02X}")

	disp.write_reg(regs.R_CLEAR_DISPLAY, 0)
	disp.write_string('Lizards rule!')

	time.sleep(1.0)
	disp.write_reg(regs.R_CLEAR_DISPLAY, 0)

    #HINT: Here we assume that none of the strings take multiple lines.
	disp.bouncy_init(5)
	disp.bouncy_set_string('Dragons!', 0, 0)
	disp.bouncy_set_string('Goat', 1, 0)
	disp.bouncy_set_string('Lion', 2, 0)
	disp.bouncy_set_string('Pony', 3, 0)
	disp.bouncy_set_string('Lizard', 4, 0)
	
	line = 0

	#Scrolls the entire view out each time
	# while True:
	# 	for row in range(disp.num_rows):
	# 		disp.bouncy_update(line, row)
	# 		line = (line + 1) % 5
	# 	time.sleep(1.0)
	
	#Scrolls only one line out each time
	while True:
		for row in range(disp.num_rows):
			disp.bouncy_update((line + row) % 5, row)
		line = (line + 1) % 5
		time.sleep(1.0)


if __name__ == "__main__":
	main()