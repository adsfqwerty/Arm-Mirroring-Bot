import serial
import struct


arduino = serial.Serial("COM3", baudrate=9600, timeout=1)
while True:
    command = input("Servo position: ")
    arduino.write(command.encode())
    from_arduino = arduino.readline()
    print(from_arduino)
