import serial
import struct
import time


arduino = serial.Serial("COM3", baudrate=9600, timeout=1)
while True:
    arduino.write(struct.pack('!B', 25))
    time.sleep(2)
    from_arduino = arduino.readline()
    from_arduino = int.from_bytes(from_arduino, "little")
    print(from_arduino)
