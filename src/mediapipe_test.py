import math
import cv2
import mediapipe as mp
def getCoords():
  mp_drawing = mp.solutions.drawing_utils
  mp_drawing_styles = mp.solutions.drawing_styles
  mp_pose = mp.solutions.pose

  image_width=1920
  image_height=1080

  # For webcam input:
  cap = cv2.VideoCapture(0)
  with mp_pose.Pose(
      min_detection_confidence=0.5,
      min_tracking_confidence=0.5) as pose:
      while cap.isOpened():
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

          def getAngle(left_shoulder, left_elbow):
            return math.atan2(left_elbow.y - left_shoulder.y, left_elbow.x - left_shoulder.x) * 180 / math.pi
          angle = getAngle(left_shoulder, left_elbow)
          
          if left_shoulder != None or left_elbow != None or angle != None:
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
        except AttributeError:
          pass

  cap.release()


if __name__ == "__main__":
  left_side = getCoords()
  print(left_side)