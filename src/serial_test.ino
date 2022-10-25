#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVOMIN  125 // this is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  575 // this is the 'maximum' pulse length count (out of 4096)

unsigned int s;
int angle;
int prev_angle;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.setTimeout(1);
  pwm.begin();
  pwm.setPWMFreq(60);
}

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    s = Serial.read();
    angle = (int)s;
    Serial.write(angle);    
    if (angle != prev_angle) {
      pwm.setPWM(12, 0, angleToPulse(angle));
      delay(200);
    }
    Serial.flush();
  }
}

int angleToPulse(int ang){
   int pulse = map(ang,0, 180, SERVOMIN,SERVOMAX);// map angle of 0 to 180 to Servo min and Servo max 
  //  Serial.println("Angle: "); Serial.print(ang);
  //  Serial.print(" pulse: "); Serial.println(pulse);
   return pulse;
}
