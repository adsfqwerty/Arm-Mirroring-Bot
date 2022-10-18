#include <Servo.h>

Servo myservo;  // create servo object to control a servo
// twelve servo objects can be created on most boards

int pos = 0;    // variable to store the servo position

String angle_str;
int angle;

void setup() {
  myservo.attach(9); // attaches the servo on pin 9 to the servo object
  Serial.begin(115200);
  Serial.setTimeout(1);
}

void loop() {
  if (Serial.available() > 0) {
      angle_str = Serial.readString();
      angle = angle_str.toInt(); // make sure angle is converted from float to int in python before sending it over to the arduino
    for (pos = 0; pos <= angle; pos += 1) { 
        // in steps of 1 degree
        myservo.write(pos); 
        delay(15);    
  }
}