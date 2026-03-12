import time
import display_1602_platform as disp
import display_1602_regs as regs

def main():
    unique_id = disp.init(0)
    if unique_id == 0:
          print("Could not find display")
          exit()

    print(f"Device ID: {disp.get_device_id():08X}")
    print(f"Unique ID: {disp.get_unique_id():08X}")
    print(f"Num rows: {disp.read_reg(regs.R_NUM_ROWS)}")
    print(f"Num columns: {disp.read_reg(regs.R_NUM_COLUMNS)}")

    disp.write_reg(regs.R_CLEAR_DISPLAY, 0)
    # disp.write_string('Dragon')
    # disp.write_reg(regs.R_CURSOR_ROW, 1)
    # disp.write_reg(regs.R_CURSOR_COL, 0)
    # disp.write_string("Goat")
    # disp.write_reg(regs.R_CURSOR_ROW, 2)
    # disp.write_reg(regs.R_CURSOR_COL, 0)
    # disp.write_string("Lion")
    # disp.write_reg(regs.R_CURSOR_ROW, 3)
    # disp.write_reg(regs.R_CURSOR_COL, 0)
    # disp.write_string("Pony")
    disp.write_string('Lizards rule!')

if __name__ == "__main__":
	main()