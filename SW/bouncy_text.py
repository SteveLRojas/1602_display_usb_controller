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
    print(f"Num rows: {disp.num_rows}")
    print(f"Num columns: {disp.num_columns}")
    print(f"Reset type: {disp.read_reg(regs.R_RESET_TYP):02X}")

    disp.write_reg(regs.R_CLEAR_DISPLAY, 0)
    disp.write_string('Lizards rule!')

    time.sleep(1.0)
    disp.write_reg(regs.R_CLEAR_DISPLAY, 0)

    disp.bouncy_init()
    lines_used = disp.bouncy_set_string('Dragons!', 0, 0)
    print(f"lines used: {lines_used}")

    while True:
        disp.bouncy_update(0)
        time.sleep(1.0)
    
    # text = "Dragons!"
    # text_len = len(text)
    # num_columns = disp.read_reg(regs.R_NUM_COLUMNS)
    # num_rows = disp.read_reg(regs.R_NUM_ROWS)
    # # in case of small displays use the entire display instead of a single line
    # if num_columns < 16:
    #     text_area = num_columns * num_rows
    # else:
    #     text_area = num_columns
    # max_offset = text_area - text_len
    # offset = 0
    # dir = 1
    
    # while True:
    #     pre_padding = ''
    #     for d in range(offset):
    #         pre_padding = pre_padding + ' '
        
    #     post_padding = ''
    #     for d in range(text_area - offset - text_len):
    #         post_padding = post_padding + ' '
        
    #     offset = offset + dir
    #     if offset == max_offset:
    #         dir = -1
    #     if offset == 0:
    #         dir = 1
        
    #     disp.write_reg(regs.R_CURSOR_COL, 0)
    #     disp.write_reg(regs.R_CURSOR_ROW, 0)
    #     disp.write_string(pre_padding + text + post_padding)
    #     time.sleep(1.0)

if __name__ == "__main__":
	main()