import serial
import time
from mediapipe_test import getCoords


def sendData(coord, br=9600, tout=1):
    arduino = serial.Serial('COM3', baudrate=br, timeout=tout)
    arduino.write(coord)
<<<<<<< HEAD

if __name__ == "__main__":
  while True:
      sendData(getCoords())
=======
>>>>>>> 422b6a198ef9ecb16bb3c1fd4206123e3da9eaf7
