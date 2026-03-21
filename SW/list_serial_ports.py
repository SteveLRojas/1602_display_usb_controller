import serial.tools.list_ports
import time

def main():
    ports = serial.tools.list_ports.comports()

    for port in ports:
        print(f"Device: {port.device}")
        print(f"Description: {port.description}")
        print(f"Hardware ID: {port.hwid}")
        if hasattr(port, 'vid') and port.vid:
            print(f"VID:PID: {port.vid:04X}:{port.pid:04X}")

if __name__ == "__main__":
	main()