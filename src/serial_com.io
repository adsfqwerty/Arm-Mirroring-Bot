#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVOMIN  125 // this is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  575 // this is the 'maximum' pulse length count (out of 4096)

// Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position

String angle_str;
int angle;

void setup() {
  myservo.attach(9); // attaches the servo on pin 9 to the servo object
  Serial.begin(9600);
  Serial.setTimeout(1);
}

void loop() {
  if (Serial.available() > 0) {
      angle_str = Serial.readString();
      angle = angle_str.toInt(); // make sure angle is converted from float to int in python before sending it over to the arduino
      Serial.print(angle);
    //for (pos = 0; pos <= angle; pos += 1) { 
        // in steps of 1 degree
    //    myservo.write(pos); 
    //    delay(5);
    //}
      for(int i=0; i<angle; i+=5) {      
          pwm.setPWM(12, 0, angleToPulse(i) );
          delay(5);
      }    
  }
}

int angleToPulse(int ang){
   int pulse = map(ang,0, 180, SERVOMIN,SERVOMAX);// map angle of 0 to 180 to Servo min and Servo max 
   Serial.print("Angle: ");Serial.print(ang);
   Serial.print(" pulse: ");Serial.println(pulse);
   return pulse;
}