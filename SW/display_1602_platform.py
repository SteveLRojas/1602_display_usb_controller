import serial
import serial.tools.list_ports
import time
import display_1602_regs as regs

baud = 1000000
ser = serial.Serial()

num_columns = 0
num_rows = 0

bouncy_text = []
bouncy_len = []
bouncy_text_area = []
bouncy_max_offset = []
bouncy_offset = []
bouncy_dir = []

def write_reg(address, value):
    address = address | 0x80
    bytes = address.to_bytes(1, 'big') + value.to_bytes(1, 'big')
    ser.write(bytes)

def read_reg(address):
    bytes = address.to_bytes(1, 'big')
    ser.write(bytes)
    response = ser.read(1)
    return int.from_bytes(response, 'big')

def get_device_id():
    response = read_reg(regs.R_DEVICE_ID_HH)
    response = (response << 8) | read_reg(regs.R_DEVICE_ID_HL) 
    response = (response << 8) | read_reg(regs.R_DEVICE_ID_LH)
    response = (response << 8) | read_reg(regs.R_DEVICE_ID_LL)
    return response

def get_unique_id():
    response = read_reg(regs.R_UNIQUE_ID_HH)
    response = (response << 8) | read_reg(regs.R_UNIQUE_ID_HL)
    response = (response << 8) | read_reg(regs.R_UNIQUE_ID_LH)
    response = (response << 8) | read_reg(regs.R_UNIQUE_ID_LL)
    return response

def write_string(string):
    num_columns = read_reg(regs.R_NUM_COLUMNS)
    num_rows = read_reg(regs.R_NUM_ROWS)
    current_column = read_reg(regs.R_CURSOR_COL)
    current_row = read_reg(regs.R_CURSOR_ROW)
    bytes = bytearray()

    for char in string:
        if (char == '\n') or (current_column >= num_columns):
            current_column = 0
            current_row += 1
            if current_row >= num_rows:
                break
            bytes.append(regs.R_CURSOR_COL | 0x80)
            bytes.append(current_column)
            bytes.append(regs.R_CURSOR_ROW | 0x80)
            bytes.append(current_row)
            if char == '\n':
                continue
        
        bytes.append(regs.R_WRITE_CHAR | 0x80)
        bytes.append(ord(char))
        current_column += 1
    ser.write(bytes)

def bouncy_init(num_lines = 0):
    num_lines = max(num_lines, num_rows)
    for d in range(num_lines):
        bouncy_text.append('')
        bouncy_len.append(0)
        bouncy_text_area.append(num_columns)
        bouncy_max_offset.append(num_columns)
        bouncy_offset.append(0)
        bouncy_dir.append(1)

def bouncy_set_string(string, line, num_lines = 0):
    bouncy_text[line] = string
    bouncy_len[line] = len(string)
    lines_used = max((bouncy_len[line] // num_columns + 1), num_lines)
    bouncy_text_area[line] = lines_used * num_columns
    bouncy_max_offset[line] = bouncy_text_area[line] - bouncy_len[line]
    if bouncy_offset[line] > bouncy_max_offset[line]:
        bouncy_offset[line] = bouncy_max_offset[line]
        bouncy_dir[line] = -1
    return lines_used

def bouncy_update(line, target_row = -1):
    pre_padding = ''
    for d in range(bouncy_offset[line]):
        pre_padding = pre_padding + ' '

    post_padding = ''
    for d in range(bouncy_text_area[line] - bouncy_offset[line] - bouncy_len[line]):
        post_padding = post_padding + ' '
    
    bouncy_offset[line] = bouncy_offset[line] + bouncy_dir[line]
    if bouncy_offset[line] == bouncy_max_offset[line]:
        bouncy_dir[line] = -1
    if bouncy_offset[line] == 0:
        bouncy_dir[line] = 1
    if target_row < 0:
        target_row = line
    bytes = bytearray()
    bytes.append(regs.R_CURSOR_COL | 0x80)
    bytes.append(0)
    bytes.append(regs.R_CURSOR_ROW | 0x80)
    bytes.append(target_row)
    ser.write(bytes)
    write_string(pre_padding + bouncy_text[line] + post_padding)

def init(unique_id):
    global num_columns
    global num_rows
    display_ports = []
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if hasattr(port, 'vid') and port.vid and (port.vid == 0x1A86) and (port.pid == 0xFE0C):
            display_ports.append(port.device)
    
    ser.baudrate = baud
    ser.dsrdtr = False
    ser.dtr = False
    ser.timeout = 1.0
    ser.write_timeout = 1.0

    for disp_port in display_ports:
        ser.port = disp_port
        ser.open()
        time.sleep(0.5)
        ser.reset_input_buffer()

        device_id = get_device_id()
        if device_id != 0x32303631:
            ser.close()
            continue
        disp_unique_id = get_unique_id()
        if unique_id and (unique_id != disp_unique_id):
            ser.close()
            continue
        num_columns = read_reg(regs.R_NUM_COLUMNS)
        num_rows = read_reg(regs.R_NUM_ROWS)
        write_reg(regs.R_CONTRAST, 45)
        write_reg(regs.R_BRIGHTNESS_R, 127)
        write_reg(regs.R_BRIGHTNESS_G, 127)
        write_reg(regs.R_BRIGHTNESS_B, 127)
        write_reg(regs.R_POWER_STATE, 0x04)
        return disp_unique_id
    return 0

def stop():
    write_reg(regs.R_CLEAR_DISPLAY, 0)
    write_reg(regs.R_BRIGHTNESS_R, 0)
    write_reg(regs.R_BRIGHTNESS_G, 0)
    write_reg(regs.R_BRIGHTNESS_B, 0)
    write_reg(regs.R_POWER_STATE, 0x00)
    ser.close()
    