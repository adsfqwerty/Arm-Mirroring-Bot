import serial
import time


def sendData(coord, br, tout=0.1):
    arduino = serial.Serial('COM3', baudrate=br, timeout=tout)
    arduino.write(coord, 'utf-8')
