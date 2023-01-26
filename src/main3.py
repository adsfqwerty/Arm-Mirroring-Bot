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

#Used to obtain angle between vectors in 3D
def getMagnitude(v):
    return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)


def calculateDotProduct(v1, v2):
    return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]

def calculateAngle3d(left_joint, main_joint, right_joint):

    vector1 = [left_joint.x-main_joint.x, left_joint.y-main_joint.y, left_joint.z-main_joint.z]
    vector2 = [right_joint.x-main_joint.x, right_joint.y-main_joint.y, right_joint.z-main_joint.z]

    dot_product = calculateDotProduct(vector1, vector2)
    v1_mag = getMagnitude(vector1)
    v2_mag = getMagnitude(vector2)

    angle = math.degrees(math.acos(dot_product/(v1_mag*v2_mag)))
    return angle



def initializeTimerVariables():
  global actual_time, current_time, desired_time
  actual_time = time.time() * 10
  current_time = math.floor(actual_time)
  desired_time = current_time + 10 #start working 1 second after

def updateTimerVariables():
  global actual_time, current_time, desired_time
  actual_time = time.time() * 10
  current_time = math.floor(actual_time)
  if current_time > desired_time:
    desired_time = current_time + 50

def getCoords():
  mp_drawing = mp.solutions.drawing_utils
  mp_drawing_styles = mp.solutions.drawing_styles
  mp_pose = mp.solutions.pose

  image_width=1920
  image_height=1080

  # For webcam input:
  cap = cv2.VideoCapture(0)

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
          global current_time, desired_time
          if current_time == desired_time:
            desired_time += 10
            
            right_shoulder = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER]
            right_elbow = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW]
            right_wrist = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST]
            right_hip = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP]
            
            
            shoulder_angle3d = calculateAngle3d(right_elbow, right_shoulder, right_hip)
            elbow_angle3d = calculateAngle3d(right_wrist, right_elbow, right_shoulder) 
            print('PRINTING ANGELS')
            print(f'Shoulder: {shoulder_angle3d}') 
            print(f'Elbow: {elbow_angle3d}')            

            
        except AttributeError:
          pass  
      
  cap.release()


if __name__ == "__main__":
  left_side = getCoords()
  print(left_side)