import math
from threading import Timer
import cv2
import mediapipe as mp
import serial
import time
import struct

#GLOBAL variable for timer
actual_time = 0
current_time = 0
desired_time = 0

def getAngle(left_joint, right_joint):
  x = -(right_joint.x - left_joint.x)   #negate values since image is flipped
  y = -(right_joint.y - left_joint.y)
  return (math.atan2(y, x) * 180 / math.pi) + 90

def initializeTimerVariables():
  global actual_time, current_time, desired_time
  actual_time = time.time()
  current_time = math.floor(actual_time)
  desired_time = current_time + 5

def updateTimerVariables():
  global actual_time, current_time, desired_time
  actual_time = time.time()
  current_time = math.floor(actual_time)
  if current_time > desired_time:
    desired_time = current_time + 5


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

  initializeTimerVariables()

  with mp_pose.Pose(
      min_detection_confidence=0.5,
      min_tracking_confidence=0.5) as pose:
      while cap.isOpened():
        updateTimerVariables()        
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
          #update the coordinates only every second
          global current_time, desired_time
          if current_time == desired_time:
            desired_time +=1
            
            right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            right_elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW]
            right_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]

            shoulder_angle = getAngle(right_shoulder, right_elbow)
            elbow_angle = getAngle(right_elbow, right_wrist)                       

            if right_shoulder != None or right_elbow != None or shoulder_angle != None or right_wrist != None or elbow_angle != None:
              #to send strings
              #arduino.write(str(math.ceil(angle)).encode())
              #shoulder_info = "shoulder " + str(math.ceil(shoulder_angle) + " ")
              #arduino.write(shoulder_info.encode())
              
              #to send int
              arduino.write(struct.pack('I', math.ceil(shoulder_angle)))

             
            #  print(
            #      f'Shoulder coordinates: ('
            #      f'{right_shoulder.x * image_width}, '
            #      f'{right_shoulder.y * image_height})'
            #  )
            #  print(
            #      f'Elbow coordinates: ('
            #      f'{right_elbow.x * image_width}, '
            #      f'{right_elbow.y * image_height})'
            #  )
              print(
                  f'Angle shoulder-elbow: '
                  f'{math.ceil(shoulder_angle)}'
              )
            #  print(
            #      f'Angle elbow-wrist: '
            #      f'{elbow_angle}'
            #  )
              arduino_read = arduino.readline()
              arduino_read = int.from_bytes(arduino_read, "little")
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