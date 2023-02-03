import cv2
import threading
import mediapipe as mp
import time
from utils import Command, Timer
import queue


class Camera():
    def __init__(self, camera, name, command):
        self.camera = camera
        self.name = name
        self.command = command
        self.cam_thread = threading.Thread(target=self.run)
        self.cam_thread.daemon = True
        self.queue_shoulder_angle_XY = queue.Queue()
        self.queue_elbow_angle_XY = queue.Queue()
        self.queue_shoulder_angle_YZ = queue.Queue()

    def displayFrame(self, image):
        cv2.imshow('MediaPipe Pose', cv2.flip(image, 1))
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
            mp.solutions.holistic.POSE_CONNECTIONS,
            landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style())
        mp_drawing.draw_landmarks(
            image,
            results.right_hand_landmarks,
            mp.solutions.holistic.HAND_CONNECTIONS)
        return image


    def run(self):

        # mp_pose = mp.solutions.pose
        # mp_hands = mp.solutions.hands
        mp_holistic = mp.solutions.holistic
        timer = Timer() # initialize timer

        with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            while self.camera.isOpened():
                timer.updateTimerVariables()
                success, image = self.camera.read()
                if not success:
                    print("Ignoring empty camera frame.")
                    # If loading a video, use 'break' instead of 'continue'.
                    break
                
                # To improve performance, optionally mark the image as not writeable to
                # pass by reference.
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = holistic.process(image)

                # Display image
                image = self.drawPose(image, results)
                self.displayFrame(image)

                # write joint coordinates
                try:
                    if timer.current_time == timer.desired_time:
                        timer.desired_time += 1

                        if self.name == "front":
                            self.command.right_shoulder = results.pose_world_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_SHOULDER]
                            self.command.right_elbow = results.pose_world_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_ELBOW]
                            self.command.right_wrist = results.pose_world_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_WRIST]
                            self.command.right_hip = results.pose_world_landmarks.landmark[mp_holistic.PoseLandmark.RIGHT_HIP]
                            self.command.left_shoulder = results.pose_world_landmarks.landmark[mp_holistic.PoseLandmark.LEFT_SHOULDER]

                    self.command.updateAngles()

                    # self.command.printDeltas()

                    # self.queue_elbow_angle_XY.put(self.command.elbow_angle)
                    # self.queue_shoulder_angle_XY.put(self.command.shoulder_angle_XY)
                    # self.queue_shoulder_angle_YZ.put(self.command.shoulder_angle_YZ)


                    if self.command.arduino_connected:
                        if self.queue_shoulder_angle_XY.qsize() == 3:
                            self.command.elbow_angle_XY = int(sum(list(self.queue_elbow_angle_XY.queue))/3)
                            self.command.shoulder_angle_XY = int(sum(list(self.queue_shoulder_angle_XY.queue))/3)
                            self.command.shoulder_angle_YZ = int(sum(list(self.queue_shoulder_angle_YZ.queue))/3)
                            self.queue_elbow_angle_XY.get()
                            self.queue_shoulder_angle_XY.get()
                            self.queue_shoulder_angle_YZ.get()

                            self.command.writeCommand()
                            self.command.readArduinoMessage()

                except AttributeError:
                    pass

            self.camera.release()


if __name__ == "__main__":
    command = Command()
    front_cam = Camera(cv2.VideoCapture(0), 'front', command) # webcam
    # side_cam = Camera(cv2.VideoCapture(1), 'side', command) # side camera
    front_cam.cam_thread.start()
    # side_cam.cam_thread.start()


    time.sleep(100)
