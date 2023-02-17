#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVOMIN  90//125 // this is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  550//575 // this is the 'maximum' pulse length count (out of 4096)

// pin# where servos are located
uint8_t shoulder_rotation_servo = 8;
uint8_t shoulder_servo = 9;
uint8_t elbow_servo = 10;
uint8_t wrist_servo = 11;
uint8_t hand_rotation_servo = 12;
uint8_t hand_servo = 13;

unsigned int s;
int prev_shoulder_rotation_servo = 0;
int prev_shoulder_servo = 0;
int prev_elbow_servo = 0;
int prev_wrist_servo = 0;
int prev_hand_rotation_servo = 0;
int prev_hand_servo = 0;

String readString;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.setTimeout(1);
  pwm.begin();
  pwm.setPWMFreq(60);
  //initiate all servos to position 0
  pwm.setPWM(shoulder_rotation_servo, 0, angleToPulse(0));
  pwm.setPWM(shoulder_servo, 0, angleToPulse(0));
  pwm.setPWM(elbow_servo, 0, angleToPulse(0));
  pwm.setPWM(wrist_servo, 0, angleToPulse(0));
  pwm.setPWM(hand_rotation_servo, 0, angleToPulse(0));
  pwm.setPWM(hand_servo, 0, angleToPulse(0));
  delay(1000);
}

/*in order to avoid incomplete rotation,
  delay must be 1 sec for rotating 180 degres
  but if the angle is less than that we can calculate
  the delay to have a smooth transition*/
int getDelay(int angle) {
  //int delay = 1000*angle/180;
  int delay = 5*angle;  //to avoid division
  return delay;
}

int angleToPulse(int ang){
   int pulse = map(ang,0, 180, SERVOMIN,SERVOMAX);// map angle of 0 to 180 to Servo min and Servo max 
  //  Serial.println("Angle: "); Serial.print(ang);
  //  Serial.print(" pulse: "); Serial.println(pulse);
   return pulse;
}

void loop() {

  //expect single strings like 700a, or 1500c, or 2000d,
  //or like 30c, or 90a, or 180d,
  //or combined like 30c,180b,70a,120d,

  if (Serial.available())  {
    char ch = Serial.read();  //gets one byte from serial buffer
    if (ch == ',') {
      if (readString.length() >1) {
        // Serial.println(readString); //prints string to serial port out

        int angle = readString.substring(1).toInt();  //convert readString into a number

        Serial.println(readString);


        if(readString.indexOf('a') == 0 && angle < 120){
          if(angle < 120 && angle > 0) {
            pwm.setPWM(shoulder_rotation_servo, 0, angleToPulse(angle));
            delay(getDelay(abs(angle-prev_shoulder_rotation_servo)));
            prev_shoulder_rotation_servo = angle;
          }
          else {
            pwm.setPWM(shoulder_rotation_servo, 0, angleToPulse(prev_shoulder_rotation_servo));
            delay(getDelay(abs(0)));
          }
        }
        if(readString.indexOf('b') == 0 && angle < 120) {
          if(angle < 120 && angle > 0) {
            pwm.setPWM(shoulder_servo, 0, angleToPulse(angle));
            delay(getDelay(abs(angle-prev_shoulder_servo)));
            prev_shoulder_servo = angle;
          }
          else {
            pwm.setPWM(shoulder_servo, 0, angleToPulse(prev_shoulder_servo));
            delay(getDelay(abs(0)));
          }
        }
        if(readString.indexOf('c') == 0 && angle < 120) {
          if(angle < 120 && angle > 0) {
            pwm.setPWM(elbow_servo, 0, angleToPulse(angle));
            delay(getDelay(abs(angle-prev_elbow_servo)));
            prev_elbow_servo = angle;
          }
          else {
            pwm.setPWM(elbow_servo, 0, angleToPulse(prev_elbow_servo));
            delay(getDelay(abs(0)));
          }
        }
        if(readString.indexOf('d') == 0 && angle < 120){ 
          if(angle < 120 && angle > 0) {
            pwm.setPWM(wrist_servo, 0, angleToPulse(angle));
            delay(getDelay(abs(angle-prev_wrist_servo)));
            prev_wrist_servo = angle;
          }
          else {
            pwm.setPWM(wrist_servo, 0, angleToPulse(prev_wrist_servo));
            delay(getDelay(abs(0)));
          }
        }
        if(readString.indexOf('e') == 0 && angle < 120) {
          if(angle < 120 && angle > 0) {
            pwm.setPWM(hand_rotation_servo, 0, angleToPulse(angle));
            delay(getDelay(abs(angle-prev_hand_rotation_servo)));
            prev_hand_rotation_servo = angle;
          }
          else {
            pwm.setPWM(hand_rotation_servo, 0, angleToPulse(prev_hand_rotation_servo));
            delay(getDelay(abs(0)));
          }
        }
        if(readString.indexOf('f') == 0 && angle < 120) {
          pwm.setPWM(hand_servo, 0, angleToPulse(angle));
          delay(getDelay(abs(angle-prev_hand_servo)));
          prev_hand_servo = angle;
        }

        readString=""; //clears variable for new input
      }
    }  
    else {     
      readString += ch; //makes the string readString
    }
  }
}