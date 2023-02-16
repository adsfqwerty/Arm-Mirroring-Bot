import time
import math
import serial

class Command():
    def __init__(self):
        self.right_shoulder = None
        self.left_shoulder = None
        self.right_elbow = None
        self.right_wrist = None
        self.right_hip = None
        
        self.shoulder_angle_XY = 0
        self.elbow_angle = 0
        self.shoulder_angle_YZ = 0
        self.fist = 0

        try:
            self.arduino = serial.Serial('COM3', baudrate=9600, timeout=1)
            self.arduino_connected = True
        except serial.SerialException:
            print("No connection to arduino detected. Continuing in 3 seconds...")
            time.sleep(3)
            self.arduino_connected = False
            pass
    
    #Used to obtain angle between vectors in 3D
    def getMagnitude(self, v):
        return math.sqrt(v[0]**2 + v[1]**2 + v[2]**2)


    def calculateDotProduct(self, v1, v2):
        return v1[0]*v2[0] + v1[1]*v2[1] + v1[2]*v2[2]
        
    def calculateAngle3d(self, left_joint, main_joint, right_joint):

        vector1 = [left_joint.x-main_joint.x, left_joint.y-main_joint.y, (left_joint.z-main_joint.z)*0.2]
        vector2 = [right_joint.x-main_joint.x, right_joint.y-main_joint.y, (right_joint.z-main_joint.z)*0.2]

        dot_product = self.calculateDotProduct(vector1, vector2)
        v1_mag = self.getMagnitude(vector1)
        v2_mag = self.getMagnitude(vector2)

        angle = math.degrees(math.acos(dot_product/(v1_mag*v2_mag)))
        return angle
    
    def getShoulderAngleXY(self):
        # Get angle between shoulder and elbow in XY plane
        return self.calculateAngle3d(self.right_elbow, self.right_shoulder, self.right_hip)

    def getElbowAngle(self):
        # Get angle between elbow and wrist in XY plane
        return self.calculateAngle3d(self.right_shoulder, self.right_elbow, self.right_wrist)

    def getShoulderAngleYZ(self):
        # Get angle between shoulder and elbow in YZ plane
        return self.calculateAngle3d(self.left_shoulder, self.right_shoulder, self.right_elbow)

    def updateAngles(self):
        # Update angles
        self.shoulder_angle_XY = self.getShoulderAngleXY()
        self.shoulder_angle_YZ = self.getShoulderAngleYZ()
        self.elbow_angle = self.getElbowAngle()
        # print('PRINTING ANGLES')
        # print(f'Shoulder XY: {self.shoulder_angle_XY}') 
        # print(f'Shoulder YZ: {self.shoulder_angle_YZ}') 
        # print(f'Elbow: {self.elbow_angle}')  
        # print('shoulder (x, y, z): ', str(round(self.right_shoulder.x, 5)) + " " +  str(round(self.right_shoulder.y, 5)) + " " + str(round(self.right_shoulder.z, 5))) 
        # print('elbow (x, y, z): ', str(round(self.right_elbow.x, 5)) + " " +  str(round(self.right_elbow.y, 5)) + " " + str(round(self.right_elbow.z, 5)))
        # print('wrist (x, y, z): ', str(round(self.right_wrist.x, 5)) + " " +  str(round(self.right_wrist.y, 5)) + " " + str(round(self.right_wrist.z, 5)))

    def printDeltas(self):
        # Print positional and angular deltas between joints
        print(
            f'Delta X: '
            f'{self.right_elbow.x - self.right_shoulder.x}\n'
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
            f'\n'
        )

    def writeCommand(self):
        if self.right_shoulder != None or self.right_elbow != None or self.shoulder_angle_XY != None or self.right_wrist != None or self.elbow_angle_XY != None:
              # Print only angles between 0 to 180
              if self.shoulder_angle_XY <= 1:
                self.shoulder_angle_XY = 1
              if self.shoulder_angle_XY > 120:
                self.shoulder_angle_XY = 120
              if self.elbow_angle_XY <= 1:
                self.elbow_angle_XY = 1
              if self.elbow_angle > 120:
                self.elbow_angle = 120
              if self.shoulder_angle_YZ <= 1:
                self.shoulder_angle_YZ = 1
              if self.shoulder_angle_YZ > 120:
                self.shoulder_angle_YZ = 120

        # Command format: motor (char), angle (int to string), end token (',' character)
        #   ex. a120, (set motor a to 120 degrees)
        #   ex. b89,  (set motor b to 89 degrees) 
        shoulder_command = 'a' + str(math.ceil(self.shoulder_angle_XY)) + ','
        elbow_command = 'c' + str(math.ceil(self.elbow_angle)) + ','
        shoulder_command_2 = 'b' + str(math.ceil(self.shoulder_angle_YZ)) + ','
        fist_command = 'f' + str(self.fist) + ','
        msg = shoulder_command + elbow_command + shoulder_command_2 + fist_command
        # msg = shoulder_command + elbow_command
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

