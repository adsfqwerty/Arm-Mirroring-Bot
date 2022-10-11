import serial
import time

usbport = 'COM3'
arduino = serial.Serial(usbport, '9600', timeout=10)        # initialize arduino at COM port, baud rate, and time for command timeout (millis)


def move(servo, angle):
    arduino.write(str(servo))
    arduino.write(angle)
    time.sleep(1)
    reachPos = str(arduino.readline())
    print('servo position is currently: {}'.format(reachPos))

while True:
    request = str(input("Input servo position: "))
    move(1, request)