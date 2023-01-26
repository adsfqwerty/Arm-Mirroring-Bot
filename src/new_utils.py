import time
import math
import serial

class Joint():
    def __init__(self, name, x, y, z):
        # Joint coordinates: name, 
        #   x: x coord
        #   y: y coord from front cam
        #   z: x coord from right side cam
        self.name = name
        self.x = x
        self.y = y
        self.z = z

class Command():
    def __init__(self):
        self.right_shoulder = Joint('right shoulder', 0, 0, 0)
        self.right_elbow = Joint('right elbow', 0, 0, 0)
        self.right_wrist = Joint('right wrist', 0, 0, 0)
        
        self.shoulder_angle_XY = 0
        self.elbow_angle_XY = 0
        self.shoulder_angle_YZ = 0

        try:
            self.arduino = serial.Serial('COM4', baudrate=9600, timeout=1)
            self.arduino_connected = True
        except serial.SerialException:
            print("No connection to arduino detected. Continuing in 3 seconds...")
            time.sleep(3)
            self.arduino_connected = False
            pass

    def getAngle(self, joint1, joint2):
        # Get inverse tangent angle from joint1 and joint2
        x = -(joint2.x - joint1.x)   #negate values since image is flipped
        y = -(joint2.y_1 - joint1.y_1)
        return (math.atan2(y, x) * 180 / math.pi) + 90

    def updateAngles(self):
        # Update angles
        self.shoulder_angle_XY = self.getAngle(self.right_shoulder, self.right_elbow)
        self.elbow_angle_XY = self.getAngle(self.right_elbow, self.right_wrist) - self.shoulder_angle_XY
        self.shoulder_angle_YZ = (math.atan2(self.right_shoulder.y_2-self.right_elbow.y_2, self.right_shoulder.z-self.right_elbow.z) * 180 / math.pi) + 90

    def printDeltas(self):
        # Print positional and angular deltas between joints
        print(
            f'Delta Y: '
            f'{self.right_elbow.y - self.right_shoulder.y}\n'
            f'Delta Z: '
            f'{self.right_elbow.z - self.right_shoulder.z}\n'
            f'Angle shoulder-elbow YZ: '
            f'{self.shoulder_angle_YZ}'
        )

    def printXYZrightShoulder(self):
        print(
            f'X: '
            f'{self.right_shoulder.x}\n'
            f'Delta Y: '
            f'{self.right_shoulder.y}\n'
            f'Delta Z: '
            f'{self.right_shoulder.z}\n'
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
        if self.right_shoulder != None or self.right_elbow != None or self.shoulder_angle_XY != None or self.right_wrist != None or self.elbow_angle_XY != None:
            # Print only angles between 0 to 180
            print(
                f'true elbow angle XY: '
                f'{self.elbow_angle_XY}'
            )
            if self.shoulder_angle_XY <= 0:
                self.shoulder_angle_XY = 0
            if self.shoulder_angle_XY > 180:
                self.shoulder_angle_XY = 180
            if self.elbow_angle_XY <= 0:
                self.elbow_angle_XY = 1
            if self.elbow_angle_XY > 180:
                self.elbow_angle_XY = 180
            if self.shoulder_angle_YZ <= 0:
                self.shoulder_angle_YZ = 1
            if self.shoulder_angle_YZ > 180:
                self.shoulder_angle_YZ = 180

            print(
                f'shoulder angle XY: '
                f'{self.shoulder_angle_XY}'
            )
            # Command format: motor (char), angle (int to string), end token (',' character)
            #   ex. a120, (set motor a to 120 degrees)
            #   ex. b89,  (set motor b to 89 degrees) 
            shoulder_command = 'a' + str(math.ceil(self.shoulder_angle_XY)) + ','
            elbow_command = 'b' + str(math.ceil(self.elbow_angle_XY)) + ','
            shoulder_command_2 = 'c' + str(math.ceil(self.shoulder_angle_YZ)) + ','
            msg = shoulder_command + elbow_command + shoulder_command_2
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

