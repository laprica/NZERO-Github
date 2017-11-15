// This file controls an Arduino Uno to test an
// NZERO NEMS Switch with the DC-TIA test.

// This file will ramp up and down around the turn on voltage
// to find the hysteresis of a given device.

// DAC used is MCP4921E, communicated with SPI

// Thanks to equaliser for a test ze used with a Teensy
// and uploaded to GitHub.
// https://gist.github.com/equaliser/8216031



// Leanna Pancoast 15 Nov 2017

#include <SPI.h>

int ledPin = 7;

int slaveSelectPin = 10;

int gatePin = 7;
int sourcePin = A0;

const byte interruptPin = 2;
volatile byte killState = LOW;
byte printKill = HIGH;

float gate_start = 0;
float gate_step = 0.1;
float gate_limit = 5;

unsigned long previousMillis = 0;
const long gate_delay = 500;

float gateV = -1;

int debugPin = 6;

// 2.8 is the 'resting' voltage. Can change to
// a moving average later.    
float sourceRest = 3.26;
float vS_thresh = 0.5;

int inByte = 0;

float mapf(float x, float in_min, float in_max, float out_min, float out_max)
{
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

void setup() {
  // Initialize the Serial to talk to PC
  Serial.begin(115200);
  Serial.setTimeout(50);

  pinMode(slaveSelectPin, OUTPUT);
  pinMode(13, OUTPUT);

  SPI.begin();
  SPI.setClockDivider(SPI_CLOCK_DIV2); // 8 MHz on Arduino Uno

  Serial.println("Ready");

  pinMode(ledPin, OUTPUT);
  pinMode(debugPin, OUTPUT);
  write_value(0);

  // setup interrupt things
  pinMode(interruptPin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(interruptPin), killCode, FALLING);

  // give Arduino time before starting
  delay(100);
}

void killCode(){
  killState = HIGH;
}

void loop() {
  digitalWrite(debugPin,HIGH);
  delay(200);
  digitalWrite(debugPin,LOW);
  delay(10);
  // Wait for python code to say OK to run
  if(killState == HIGH){
    if(printKill){
      Serial.println("stopped");
    }
    printKill = LOW;
  }
  if (Serial.available() > 0) {
    // get incoming byte:
    inByte = Serial.read();

    switch (inByte) {
      case 'p':
        delay(10);
        // Parameters are being input
        // Gate start, gate step, gate end
        if (Serial.available() > 0) {
          gate_start = Serial.read();
        }
        if (Serial.available() > 0) {
          gate_step = Serial.read();
        }
        if (Serial.available() > 0) {
          gate_limit = Serial.read();
        }
        Serial.println("received parameters");
        break;
      case 'b':
        // Begin the sweep
        int worked = 1;
        gateV = gate_start;

        int contLoop = 1;

        digitalWrite(ledPin, HIGH);
        delay(250);
        digitalWrite(ledPin, LOW);
        delay(250);
        digitalWrite(ledPin, HIGH);
        delay(250);
        digitalWrite(ledPin, LOW);
        delay(250);
        digitalWrite(ledPin, HIGH);
        delay(250);
        digitalWrite(ledPin, LOW);
        delay(250);
        digitalWrite(ledPin, HIGH);
        
        while(contLoop){
          // check if should stop the process
          if( killState == HIGH ){
            write_value(0);
            contLoop = 0;
            Serial.println("state killed");
            break;
          }
          
          // check if should continue loop
          if ( Serial.available() > 0 ) {
            inByte = Serial.read();
            // s will be sent in ctrl+c case
            if (inByte == 's') {
              write_value(0);
              contLoop = 0;
              break;
            }
          }

          Serial.println("loop");

          // start ramp up
          int ru = rampUp();

          if(!ru){
            // something wrong happened, get out of loop
            Serial.println("ramp up failed");
            break;
          }

          // start ramp down
          int rd = rampDown();
          
          if(!rd){
            // something wrong happened, get out of loop
            Serial.println("ramp down failed");
            break;
          }
        }

        // exited loop, now set output to 0 V
        write_value(0);
        Serial.println("End program");
    }
  }
}

int rampUp(){
  // will return 1 on success
  // return 0 on not success
  // This function will ramp the gate voltage up until
  // the devices switches or the gate voltage reaches the limit

  // check the source voltage
  float sourceV = getSourceVolt();
  
  if( abs(sourceRest - sourceV) > vS_thresh ){
    // the switch is shorted from the start
    Serial.print("Shorted from the start with: ");
    Serial.print(sourceV);
    Serial.println(" V");
    return 0;
  }

  // check if out of bounds to ramp up
  if ( gateV - gate_limit > 0){
    Serial.println("Open Switch");
    write_value(0);
    return 0;
  }

  // good to start the ramp up
  while( gateV - gate_limit < 0 ) {
    digitalWrite(debugPin,HIGH);
  delay(200);
  digitalWrite(debugPin,LOW);
  delay(10);
    // check if should stop the process
    if( killState == HIGH){
      write_value(0);
      Serial.println("state killed in ramp up");
      return;
    }

    unsigned long currentMillis = millis();

    // increase gate voltage
    if(currentMillis - previousMillis >= gate_delay){
      previousMillis = currentMillis;
      Serial.print("gate V: ");
      Serial.println(gateV);
      gateV += gate_step;
      write_value(gateV);
      Serial.print("Source volt: ");
      Serial.println(sourceV);
    }
    
    // look at source voltage to see if switch
    sourceV = getSourceVolt();
    
    if( abs(sourceRest - sourceV) > vS_thresh ){
      // then the device has closed!
      Serial.print("Closed at ");
      Serial.print(gateV);
      Serial.print(" V with ");
      Serial.print(sourceV);
      Serial.println(" V on source");
      return 1;
    }
  }
  Serial.println("Reached limit, open switch");
  return 0;
}


int rampDown(){
  // will return 1 on success
  // return 0 on not success
  // This function will ramp the gate voltage up until
  // the devices opens or the gate voltage goes below 0

  // check the source voltage
  float sourceV = getSourceVolt();
  
  if( abs(sourceRest - sourceV) < vS_thresh ){
    // the switch is shorted from the start
    Serial.print("Open from start of Ramp Down with ");
    Serial.print(sourceV);
    Serial.println(" V");
    return 0;
  }

  // check if out of bounds to ramp up
  if ( gateV < 0){
    Serial.println("Not Opening");
    return 0;
  }

  // good to start the ramp down
  while( gateV > 0 ) {
    
    // check if should stop the process
    if( killState == HIGH){
      write_value(0);
      Serial.println("state killed in ramp down");
      return;
    }

    unsigned long currentMillis = millis();
    
    // decrease gate voltage if time is correct
    if(currentMillis - previousMillis >= gate_delay){
      previousMillis = currentMillis;
      Serial.print("gate V: ");
      Serial.println(gateV);
      
      gateV -= gate_step;
      write_value(gateV);
      Serial.print("Source volt: ");
      Serial.println(sourceV);
    }

    // look at source voltage to see if switch
    sourceV = getSourceVolt();
    
    if( abs(sourceRest - sourceV) - vS_thresh < 0 ){
      // then the device has opened!
      Serial.print("Opened at ");
      Serial.print(gateV);
      Serial.print(" V with ");
      Serial.print(sourceV);
      Serial.println(" V on source");
      return 1;
    }
  }
  Serial.println("Reached 0, closed switch");
  return 0;
}


float getSourceVolt(){
  // This function will return the voltage the Arduino is reading
  // on the given source pin.
  int vS = analogRead(sourcePin);
  // map to get real voltage number
  float vSa = mapf(vS, 0, 1023, 0, 5);
  return vSa;
}

void write_value(float value) {
  // channel (0 = DACA, 1 = DACB) // Vref input buffer (0 = unbuffered, 1 = buffered) // gain (1 = 1x, 0 = 2x)  // Output power down power down (0 = output buffer disabled) //  12 bits of data
  // TODO: Check if changing from float to int is necessary
  value = value / 20.0;
  int v = value;
  uint16_t out = (0 << 15) | (1 << 14) | (1 << 13) | (1 << 12) | (v);
  digitalWrite(slaveSelectPin, LOW);
  SPI.transfer(out >> 8);         //you can only put out one byte at a time so this is splitting the 16 bit value.
  SPI.transfer(out & 0xFF);
  digitalWrite(slaveSelectPin, HIGH);
}
