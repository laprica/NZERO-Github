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

int slaveSelectPin = 10;

int gatePin = 7;
int sourcePin = A0;

float gate_start = 0;
float gate_step = 0.2;
float gate_limit = 50;

float vGa = -1;

float vS_thresh = 0.3;

int inByte = 0;

float mapf(float x, float in_min, float in_max, float out_min, float out_max)
{
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

void setup() {

  // Initialize the Serial to talk to PC
  Serial.begin(9600);
  Serial.setTimeout(50);

  pinMode(slaveSelectPin, OUTPUT);

  SPI.begin();
  SPI.setClockDivider(SPI_CLOCK_DIV2); // 8 MHz on Arduino Uno

  Serial.println("Ready");

  pinMode(13, OUTPUT);
  write_value(0);

  delay(100);
}

void loop() {
  // Wait for python code to say OK to run
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
        float vG = gate_start;

        int contLoop = 1;
        
        while(contLoop){
          // check if should continue loop
          if (Serial.available() > 0) {
            inByte = Serial.read();
            if (inByte == 's') {
              write_value(0);
              contLoop = 0;
              break;
            }
          }

          // start ramp up
          int ru = rampUp(vG);

          if(!ru){
            // something wrong happened, get out of loop
            break;
          }

          // start ramp down
          int rd = rampDown(vG);
          
          if(!rd){
            // something wrong happened, get out of loop
            break;
          }
        
          delay(500);

          Serial.println("loop");
        }

        // exited loop, now set output to 0 V
        write_value(0);
    }
  }
}

int rampUp(float gateV){
  // will return 1 on success
  // return 0 on not success
  // This function will ramp the gate voltage up until
  // the devices switches or the gate voltage reaches the limit

  // check the source voltage
  float sourceV = getSourceVolt();
  if( abs(2.8 - sourceV) > vS_thresh ){
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

    // increase gate voltage
    gateV += gate_step;
    write_value(gateV);

    // look at source voltage to see if switch
    sourceV = getSourceVolt();
    
    if( abs(2.8 - sourceV) > vS_thresh ){
      // then the device has closed!
      Serial.print("Closed at ");
      Serial.print(gateV);
      Serial.print(" V with ");
      Serial.print(sourceV);
      Serial.println(" V on source");
      return 1;
    }
  }
  return 0;
}


int rampDown(float gateV){
  // will return 1 on success
  // return 0 on not success
  // This function will ramp the gate voltage up until
  // the devices opens or the gate voltage goes below 0

  // check the source voltage
  float sourceV = getSourceVolt();
  if( abs(2.8 - sourceV) < vS_thresh ){
    // the switch is shorted from the start
    Serial.print("Shorted from the start with: ");
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

    // decrease gate voltage
    gateV -= gate_step;
    write_value(gateV);

    // look at source voltage to see if switch
    sourceV = getSourceVolt();
    
    if( abs(2.8 - sourceV) < vS_thresh ){
      // then the device has opened!
      Serial.print("Opened at ");
      Serial.print(gateV);
      Serial.print(" V with ");
      Serial.print(sourceV);
      Serial.println(" V on source");
      return 1;
    }
  }
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
  value = value / 20.0;
  int v = value;
  uint16_t out = (0 << 15) | (1 << 14) | (1 << 13) | (1 << 12) | (v);
  digitalWrite(slaveSelectPin, LOW);
  //Serial.print("out: ");
  //Serial.println(out);
  SPI.transfer(out >> 8);         //you can only put out one byte at a time so this is splitting the 16 bit value.
  SPI.transfer(out & 0xFF);
  digitalWrite(slaveSelectPin, HIGH);
}
