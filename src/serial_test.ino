#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVOMIN  90//125 // this is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  550//575 // this is the 'maximum' pulse length count (out of 4096)

// pin# where servos are located
uint8_t shoulder_servo = 12;
uint8_t elbow_servo = 13;

unsigned int s;
int prev_angle_shoulder = 0;
int prev_angle_elbow = 0;

String readString;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.setTimeout(1);
  pwm.begin();
  pwm.setPWMFreq(60);
  //initiate all servos to position 0
  pwm.setPWM(shoulder_servo, 0, angleToPulse(0));
  pwm.setPWM(elbow_servo, 0, angleToPulse(0));
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

// void loop() {
//   // put your main code here, to run repeatedly:
//   if (Serial.available() > 0) {
//     s = Serial.read();
//     angle = (int)s;
//     Serial.write(angle);    
//     if (angle > 0) {
//       pwm.setPWM(shoulder_servo, 0, angleToPulse(angle));
//       prev_angle = angle
//       delay(getDelay(abs(angle-prev_angle)));
//     }
//     Serial.flush();
//   }
// }

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
    char c = Serial.read();  //gets one byte from serial buffer
    if (c == ',') {
      if (readString.length() >1) {
        Serial.println(readString); //prints string to serial port out

        int angle = readString.substring(1).toInt();  //convert readString into a number


        Serial.print("writing Angle: ");
        Serial.println(angle);
        if(readString.indexOf('a') > 0){ 
          pwm.setPWM(shoulder_servo, 0, angleToPulse(angle));
          delay(getDelay(abs(angle-prev_angle_shoulder));
          prev_angle_shoulder = angle;
        }
        if(readString.indexOf('b') >0) {
          pwm.setPWM(13, 0, angleToPulse(angle));
          delay(getDelay(abs(angle-prev_angle_elbow));
          prev_angle_elbow = angle;
        }

        readString=""; //clears variable for new input
      }
    }  
    else {     
      readString += c; //makes the string readString
    }
  }
}