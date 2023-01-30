import math
from threading import Timer
import cv2
import mediapipe as mp
from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QLabel
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
import sys
import time

#GLOBAL variable for timer
actual_time = 0
current_time = 0
desired_time = 0

class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(300, 100)
        self.setWindowTitle("CodersLegacy")
        self.setWindowIcon(QIcon("icon.jpg"))
 
        layout = QVBoxLayout()
        self.setLayout(layout)
 
        label = QLabel("Hello World")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

    def changeLabel(self, text):
        self.label = QLabel(text)

def getAngle(left_joint, right_joint):
  x = -(right_joint.x - left_joint.x)   #negate values since image is flipped
  y = -(right_joint.y - left_joint.y)
  return (math.atan2(y, x) * 180 / math.pi) + 90

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

def launchWindow(text):
    app = QApplication(sys.argv)
    window = Window()
    window.changeLabel(text)
    window.show()
    sys.exit(app.exec())

def formatZ(raw_z):
    empty = '.'
    # empty = 'abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOPQRSTUVWX'
    mid = 50
    visualize_shoulder = int(raw_z * 30)
    i = 0
    while i < mid+visualize_shoulder:
        empty = empty + "."
        i += 1
    empty = empty + "O"
    while i < 100:
        empty = empty + "."
        i += 1
    return empty

def createVisualizer(shoulder_z, elbow_z, wrist_z):
    shoulder_string = formatZ(shoulder_z)
    elbow_string = formatZ(elbow_z)
    wrist_string = formatZ(wrist_z)
    # print(shoulder_string)
    visualizer = "shoulder z: " + str(round(shoulder_z,5)) + "\t" + shoulder_string + "\nelbow z: " + str(round(elbow_z,5)) + "\t" + elbow_string + "\nwrist_z: " + str(round(wrist_z,5)) + "\t" + wrist_string
    print(visualizer)


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
            #update the coordinates only every  half second
            global current_time, desired_time
            # if current_time == desired_time:

            desired_time +=1
        
            right_shoulder_z = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].z
            right_elbow_z = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW].z
            right_wrist_z = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].z
            # print(right_shoulder_z)

            createVisualizer(right_shoulder_z, right_elbow_z, right_wrist_z)                    
        except AttributeError:
          pass  
        time.sleep(0.5)
  cap.release()


if __name__ == "__main__":
  left_side = getCoords()
  print(left_side)