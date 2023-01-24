import time
import math
import serial

class Command():
    def __init__(self):
        self.right_shoulder_x = 0
        self.right_shoulder_y_front = 0
        self.right_shoulder_y_side = 0
        self.right_shoulder_z = 0
        self.right_elbow_x = 0
        self.right_elbow_y_front = 0
        self.right_elbow_y_side = 0
        self.right_elbow_z = 0
        self.right_wrist_x = 0
        self.right_wrist_y_front = 0
        self.right_wrist_y_side = 0
        self.right_wrist_z = 0
        
        self.shoulder_angle_XY = 0
        self.elbow_angle_XY = 0
        self.shoulder_angle_XZ = 0

        try:
            self.arduino = serial.Serial('COM3', baudrate=9600, timeout=1)
            self.arduino_connected = True
        except serial.SerialException:
            print("No connection to arduino detected. Continuing in 3 seconds...")
            time.sleep(3)
            self.arduino_connected = False
            pass

    def getTangent(self, joint1_x, joint2_x, joint1_y, joint2_y):
        # Get inverse tangent angle from joint 1 and joint 2
        x = -(joint1_x - joint2_x)   #negate values since image is flipped
        y = -(joint1_y - joint2_y)
        return math.atan2(y, x) * 180 / math.pi + 90
    
    def getShoulderAngleXY(self):
        # Get angle between shoulder and elbow in XY plane
        return self.getTangent(self.right_shoulder_x, self.right_elbow_x, self.right_shoulder_y_front, self.right_elbow_y_front)

    def getElbowAngleXY(self):
        # Get angle between elbow and wrist in XY plane
        return self.getTangent(self.right_elbow_x, self.right_wrist_x, self.right_elbow_y_front, self.right_wrist_y_front)

    def getShoulderAngleYZ(self):
        # Get angle between shoulder and elbow in YZ plane
        return self.getTangent(self.right_shoulder_z, self.right_elbow_z, self.right_shoulder_y_side, self.right_elbow_y_side)

    def updateAngles(self):
        # Update angles
        self.shoulder_angle_XY = self.getShoulderAngleXY()
        print(
            f'shoulder XY angle: '
            f'{self.shoulder_angle_XY}'
            )
        print(
            f'elbow XY angle: '
            f'{self.elbow_angle_XY}'
            )
        self.elbow_angle_XY = self.getElbowAngleXY()
        # self.shoulder_angle_YZ = self.getShoulderAngleYZ()

    def printDeltas(self):
        # Print positional and angular deltas between joints
        print(
            f'Delta X: '
            f'{self.right_elbow_x - self.right_shoulder_x}\n'
        #     f'Delta Z: '
        #     f'{self.right_elbow_z - self.right_shoulder_z}\n'
        #     f'Angle shoulder-elbow YZ: '
        #     f'{self.shoulder_angle_YZ}'
        )

    def readArduinoMessage(self):
        # Read arduino messages
        arduino_read = self.arduino.readline()
        arduino_read = arduino_read.decode()
        print(
            f'Arduino is receiving: '
            f'{arduino_read}'
        )

    def writeCommand(self):
        if self.right_shoulder_x != None or self.right_shoulder_y_front != None or self.right_shoulder_y_side != None or self.right_elbow_x != None or self.right_elbow_y_front != None or self.right_elbow_y_side != None or self.shoulder_angle_XY != None or self.right_wrist_x != None or self.right_wrist_y_front != None or self.right_wrist_y_side != None or self.elbow_angle_XY != None:
              # Print only angles between 0 to 180
              if self.shoulder_angle_XY <= 0:
                self.shoulder_angle_XY = 1
              if self.shoulder_angle_XY > 180:
                self.shoulder_angle_XY = 180
              if self.elbow_angle_XY <= 0:
                self.elbow_angle_XY = 1
              if self.elbow_angle_XY > 180:
                self.elbow_angle_XY = 180
            #   if self.shoulder_angle_YZ <= 0:
            #     self.shoulder_angle_YZ = 1
            #   if self.shoulder_angle_YZ > 180:
            #     self.shoulder_angle_YZ = 180

        # Command format: motor (char), angle (int to string), end token (',' character)
        #   ex. a120, (set motor a to 120 degrees)
        #   ex. b89,  (set motor b to 89 degrees) 
        shoulder_command = 'a' + str(math.ceil(self.shoulder_angle_XY)) + ','
        elbow_command = 'b' + str(math.ceil(self.elbow_angle_XY)) + ','
        # shoulder_command_2 = 'c' + str(math.ceil(self.shoulder_angle_YZ)) + ','
        # msg = shoulder_command + elbow_command + shoulder_command_2
        msg = shoulder_command + elbow_command
        print(msg)

        self.arduino.write(bytes(msg.encode()))


class Timer():
    # Timer between commands so serial line does not get overloaded
    def __init__(self):
        self.actual_time = time.time() * 10 # use deciseconds instead of seconds
        self.current_time = math.floor(self.actual_time)
        self.desired_time = self.current_time + 10
    
    def updateTimerVariables(self):
        self.actual_time = time.time() * 10
        self.current_time = math.floor(self.actual_time)
        if self.current_time > self.desired_time:
            self.desired_time = self.current_time + 5

