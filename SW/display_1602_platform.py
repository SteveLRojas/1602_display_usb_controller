import serial
import serial.tools.list_ports
import time
from queue import Queue
import display_1602_regs as regs

baud = 1000000
ser = serial.Serial()

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

    for char in string:
        if char == '\n':
            current_column = 0
            current_row += 1
            if current_row >= num_rows:
                break
            write_reg(regs.R_CURSOR_COL, current_column)
            write_reg(regs.R_CURSOR_ROW, current_row)
            continue

        # If we reach the end of the line, move to the next one
        if current_column >= num_columns:
            current_column = 0
            current_row += 1

            # Stop if we reach the bottom of the display
            if current_row >= num_rows:
                break

            write_reg(regs.R_CURSOR_COL, current_column)
            write_reg(regs.R_CURSOR_ROW, current_row)

        write_reg(regs.R_WRITE_CHAR, ord(char))
        current_column += 1

def init(unique_id):
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
        return disp_unique_id
    return 0
