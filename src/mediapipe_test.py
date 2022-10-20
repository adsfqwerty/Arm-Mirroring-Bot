import math
from threading import Timer
import cv2
import mediapipe as mp
import serial
import time
import struct

#variable for timer
actual_time = 0
current_time = 0
desired_time = 0

def getAngle(left_shoulder, left_elbow):
  return math.atan2(left_elbow.y - left_shoulder.y, left_elbow.x - left_shoulder.x) * 180 / math.pi

def getCoords():
  mp_drawing = mp.solutions.drawing_utils
  mp_drawing_styles = mp.solutions.drawing_styles
  mp_pose = mp.solutions.pose

  image_width=1920
  image_height=1080

  # For webcam input:
  cap = cv2.VideoCapture(0)
  #serial communication for windows
  arduino = serial.Serial('COM3', baudrate=9600, timeout=1)
  #serial communication for linux
  #arduino = serial.Serial('/dev/ttyUSB0', baudrate=9600, timeout=1)

  #initialize timer variables
  actual_time = time.time()
  current_time = math.floor(actual_time)
  desired_time = current_time + 5

  with mp_pose.Pose(
      min_detection_confidence=0.5,
      min_tracking_confidence=0.5) as pose:
      while cap.isOpened():
        #update timer variables
        actual_time = time.time()
        current_time = math.floor(actual_time)
        if current_time > desired_time:
          desired_time = current_time + 5
        
        success, image = cap.read()
        if not success:
          print("Ignoring empty camera frame.")
          # If loading a video, use 'break' instead of 'continue'.
          continue

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = pose.process(image)

        # Draw the pose annotation on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        # Flip the image horizontally for a selfie-view display.
        cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))
        if cv2.waitKey(5) & 0xFF == 27:
          break
        try:
          left_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER]
          left_elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW]

          angle = getAngle(left_shoulder, left_elbow)
          
          #update the coordinates only every second
          if current_time == desired_time:
            desired_time +=1

            if left_shoulder != None or left_elbow != None or angle != None:
              
              arduino.write(str(math.ceil(angle)).encode()) 
            #   arduino.write(struct.pack('>B', math.ceil(angle)))
              #time.sleep(0.5)
              print(
                  f'Left Shoulder coordinates: ('
                  f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].x * image_width}, '
                  f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_SHOULDER].y * image_height})'
              )
              print(
                  f'Left Elbow coordinates: ('
                  f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW].x * image_width}, '
                  f'{results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ELBOW].y * image_height})'
              )
              print(
                  f'Left Angle in degrees: '
                  f'{angle}'
              )
              arduino_read = arduino.readline()
              print(
                  f'Arduino is receiving: '
                  f'{arduino_read}'
              )
        except AttributeError:
          pass
  
      
  cap.release()


if __name__ == "__main__":
  left_side = getCoords()
  print(left_side)