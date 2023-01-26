import cv2
import threading
import mediapipe as mp
import time
from utils import Command, Timer
import threading

# lock = threading.Lock()


class Camera():
    def __init__(self, camera, name, command):
        self.camera = camera
        self.name = name
        self.command = command
        self.cam_thread = threading.Thread(target=self.run)
        self.cam_thread.daemon = True

    def displayFrame(self, image):
        title = 'MediaPipe Pose ' + self.name
        cv2.imshow(title, cv2.flip(image, 1))
        if cv2.waitKey(5) & 0xFF == 27:
            print("Cannot display frame")
            return None

    def drawPose(self, image, results):
        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles

        # Draw the pose annotation on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp.solutions.pose.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        return image

    def run(self):

        mp_pose = mp.solutions.pose
        timer = Timer() # initialize timer

        with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
            while self.camera.isOpened():
                timer.updateTimerVariables()
                success, image = self.camera.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    # If loading a video, use 'break' instead of 'continue'.
                    break
                
                # To improve performance, optionally mark the image as not writeable to
                # pass by reference.
                image.flags.writeable = False
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = pose.process(image)

                # Display image
                image = self.drawPose(image, results)
                self.displayFrame(image)

                # write joint coordinates
                try:
                    if timer.current_time == timer.desired_time:
                        timer.desired_time += 1
                        if self.name == "front":
                            # lock.acquire()
                            self.command.right_shoulder.x = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].x
                            self.command.right_shoulder.y = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].y
                            self.command.right_shoulder.z = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_SHOULDER].z

                            self.command.right_wrist.x = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].x
                            self.command.right_wrist.y = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].y
                            self.command.right_wrist.z = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_WRIST].z

                            self.command.right_elbow.x = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW].x
                            self.command.right_elbow.y = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW].y
                            self.command.right_elbow.z = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ELBOW].z
                            # lock.release()

                    self.command.updateAngles()

                    # self.command.printDeltas()
                    # self.command.readArduinoMessage()

                    if self.command.arduino_connected == True:
                        print('writing command...')
                        self.command.writeCommand()


                except AttributeError:
                    pass

            self.camera.release()


if __name__ == "__main__":
    command = Command()
    front_cam = Camera(cv2.VideoCapture(0, cv2.CAP_DSHOW), 'front', command) # webcam
    # side_cam = Camera(cv2.VideoCapture(1, cv2.CAP_DSHOW), 'side', command) # side camera
    front_cam.cam_thread.start()
    # side_cam.cam_thread.start()

    time.sleep(100)
