#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver();

#define SERVOMIN  90//125 // this is the 'minimum' pulse length count (out of 4096)
#define SERVOMAX  550//575 // this is the 'maximum' pulse length count (out of 4096)

// pin# where servos are located
uint8_t shoulder_servo = 12;

unsigned int s;
int angle;
int prev_angle;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  Serial.setTimeout(1);
  pwm.begin();
  pwm.setPWMFreq(60);
  //initiate all servos to position 0
  pwm.setPWM(shoulder_servo, 0, angleToPulse(0));
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

void loop() {
  // put your main code here, to run repeatedly:
  if (Serial.available() > 0) {
    s = Serial.read();
    angle = (int)s;
    Serial.write(angle);    
    if (angle > 0) {
      pwm.setPWM(shoulder_servo, 0, angleToPulse(angle));
      prev_angle = angle
      delay(getDelay(abs(angle-prev_angle)));
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
