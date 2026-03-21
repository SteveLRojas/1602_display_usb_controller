import serial
import time

port = "/dev/ttyACM0"
baud = 1000000
ser = serial.Serial()

def main():
    ser.baudrate = baud
    ser.dsrdtr = False
    ser.dtr = False
    ser.timeout = 1.0
    ser.write_timeout = 1.0
    ser.port = port
    ser.open()
    time.sleep(0.5)
    ser.reset_input_buffer()

    data = bytes(64)          # 64 zero bytes
    ser.write(data)
    ser.flush()

    time.sleep(0.1)
    data = bytes(64)          # 64 zero bytes
    ser.write(data)
    ser.flush()

    time.sleep(0.1)
    ser.write(b'bweep\r\n')
    ser.flush()  # Don't wait for buffer

if __name__ == "__main__":
	main()