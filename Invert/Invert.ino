#define EI_ARDUINO_INTERRUPTED_PIN
#include <EnableInterrupt/EnableInterrupt.h>
// The variable is arduinoInterruptedPin and it is of type uint8_t

void intChange()
{
  uint8_t op;
  // Read the level and negate the output
  digitalWrite(8, op=!digitalRead(9));
  digitalWrite(13, op); // Toggle the LED
}

// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin 13 as an output.
  pinMode(13, OUTPUT);
  pinMode(9, INPUT);
  pinMode(8, OUTPUT);

  digitalWrite(9, LOW); // Pull down
  digitalWrite(13, LOW);
  digitalWrite(8, HIGH);

  enableInterrupt( 9 , intChange, CHANGE);
}

// the loop function runs over and over again forever
void loop() {
  digitalWrite(13, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(50);              // wait for a second
  digitalWrite(13, LOW);    // turn the LED off by making the voltage LOW
  delay(2000);              // wait for a second
}
