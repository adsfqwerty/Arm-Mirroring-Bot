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

def getAngle_XY(left_joint, right_joint):
  x = -(right_joint.x - left_joint.y)   #negate values since image is flipped
  y = -(right_joint.y - left_joint.y)
  return (math.atan2(y, x) * 180 / math.pi) + 90

def getAngle_YZ(left_joint, right_joint):
  y = -(right_joint.y - left_joint.y)   #negate values since image is flipped
  z = -(right_joint.z - left_joint.z)
  return (math.atan2(y, z) * 180 / math.pi) + 90



def initializeTimerVariables():
  global actual_time, current_time, desired_time
  actual_time = time.time() * 10 #use deciseconds instead of seconds
  current_time = math.floor(actual_time)
  desired_time = current_time + 10

def updateTimerVariables():
  global actual_time, current_time, desired_time
  actual_time = time.time() * 10
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
  '''
  arduino = serial.Serial('COM3', baudrate=9600, timeout=1)
  '''
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
          #update the coordinates only every  half second
          global current_time, desired_time
          if current_time == desired_time:

            desired_time +=1
            
            right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            right_elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW]
            right_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]

            shoulder_angle_XY = getAngle_XY(right_shoulder, right_elbow)
            elbow_angle_XY = getAngle_XY(right_elbow, right_wrist)

            shoulder_angle_YZ = getAngle_YZ(right_shoulder.y, right_elbow)
            elbow_angle_YZ = getAngle_YZ(right_elbow, right_wrist)                 

            '''
            if right_shoulder != None or right_elbow != None or shoulder_angle_XY != None or right_wrist != None or elbow_angle_XY != None or shoulder_angle_YZ != None or right_wrist != None or elbow_angle_YZ != None:
              #print only angles between 0 to 180
              if shoulder_angle_XY <= 0:
                shoulder_angle_XY = 1
              if shoulder_angle_XY > 180:
                shoulder_angle_XY = 180
              if elbow_angle_XY <= 0:
                elbow_angle_XY = 1
              if elbow_angle_XY > 180:
                elbow_angle_XY = 180

              if shoulder_angle_YZ <= 0:
                shoulder_angle_YZ = 1
              if shoulder_angle_YZ > 180:
                shoulder_angle_YZ = 180
              if elbow_angle_YZ <= 0:
                elbow_angle_YZ = 1
              if elbow_angle_YZ > 180:
                elbow_angle_YZ = 180
            '''
              #to send strings
              #arduino.write(str(math.ceil(angle)).encode())
              #shoulder_info = "shoulder " + str(math.ceil(shoulder_angle_XY) + " ")
              #arduino.write(shoulder_info.encode())
              
              
              # #to send as string
              # shoulder_command = 'a' + str(math.ceil(shoulder_angle_XY)) + ','
              # # shoulder_command = shoulder_command.encode('utf-8')
              # #arduino.write(struct.pack('s', shoulder_command))
              # elbow_command = 'b' + str(math.ceil(elbow_angle_XY)) + ','
              # # elbow_command = elbow_command.encode('utf-8')
              # command = shoulder_command + elbow_command
              # #arduino.write(struct.pack('s', elbow_command))
              # # arduino.write(struct.pack('s', shoulder_command+elbow_command))
              

              
              # arduino.write(bytes(command.encode()))
              

              #arduino.write(struct.pack('I', math.ceil(elbow_angle_XY + 200)))

             
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
                  f'Angle shoulder-elbow XY: '
                  f'{math.ceil(shoulder_angle_XY)}'
              )
            print(
                f'Angle elbow-wrist XY: '
                f'{elbow_angle_XY}'
            )
            print(
                  f'Angle shoulder-elbow YZ: '
                  f'{math.ceil(shoulder_angle_YZ)}'
              )
            print(
                f'Angle elbow-wrist YZ: '
                f'{elbow_angle_YZ}'
            )
            # arduino_read = arduino.readline()
            # arduino_read = arduino_read.decode()
            # print(
            #     f'Arduino is receiving: '
            #     f'{arduino_read}'
            # )
        except AttributeError:
          pass  
      
  cap.release()


if __name__ == "__main__":
  left_side = getCoords()
  print(left_side)