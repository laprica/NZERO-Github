// This file controls an Arduino Uno to test an
// NZERO NEMS Switch with the DC-TIA test.

// This file will ramp up and down around the turn on voltage
// to find the hysteresis of a given device.

// DAC used is MCP4921E, communicated with SPI

// Thanks to equaliser for a test ze used with a Teensy
// and uploaded to GitHub.
// https://gist.github.com/equaliser/8216031



// Leanna Pancoast 15 Nov 2017

#define DEBUG

#include <SPI.h>

#ifdef DEBUG
#define DEBUG_PRINT(x)     Serial.print (x)
#define DEBUG_PRINTDEC(x)     Serial.print (x, DEC)
#define DEBUG_PRINTLN(x)  Serial.println (x)
#else
#define DEBUG_PRINT(x)
#define DEBUG_PRINTDEC(x)
#define DEBUG_PRINTLN(x) 
#endif 

// initialize hardware pins
int ledPin = 7;

int slaveSelectPin = 10;

int gatePin = 7;
int sourcePin = A0;
int resetPin = 5;

// initialize info for stopping processes
const byte interruptPin = 2;
volatile byte killState = LOW;
byte rfReady = 0;
byte printKill = HIGH;

// variable to keep track of time passed for bias increase
unsigned long previousMillis = 0;


uint16_t ftou(float x){
  // This function converts a float to a uint16_t that will
  // be written to the MCP4921E DAC
    return x * (4096 / 5.0);
}

float utof(uint16_t x){
  // This function converts a uint16_t that will
  // be written to the MCP4921E DAC to a more readable float
    return x * (5.0/4096);
}

// initialize testing parameters
uint16_t gate_start = ftou(0/19.5);
uint16_t gate_step = 1;
uint16_t gate_limit = ftou(50.0/19.5);

// delay in ms
const long gate_delay = 200;

// reset pulse length in ms
int resetLength = 1;

// 2.78 is the 'resting' voltage. Can change to
// a moving average later.    
float sourceRest = 2.78;
float vS_thresh = 0.03;

// number of open cycles before determining a switch as open
int numOC = 10;

// Variable to keep track of gate voltage
uint16_t gateV = 0;

// variable to receive from Serial
int inByte = 0;



float mapf(float x, float in_min, float in_max, float out_min, float out_max){
  // This function changes a number in a range to a number in a different range.
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

void setup() {
  // Initialize the Serial to talk to PC
  Serial.begin(115200);
  Serial.setTimeout(50);

  pinMode(slaveSelectPin, OUTPUT);
  pinMode(13, OUTPUT);
  pinMode(resetPin, OUTPUT);

  SPI.begin();
  SPI.setClockDivider(SPI_CLOCK_DIV2); // 8 MHz on Arduino Uno

  // Initialize led pin
  pinMode(ledPin, OUTPUT);

  // initialize DAC to 0 V
  write_value(0);

  // Setup KILL clicky switch intterupt
  pinMode(interruptPin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(interruptPin), killCode, FALLING);

  // Tell the user the Arduino is ready
  Serial.println("Ready BUH v1.3");

  // give Arduino time before starting
  delay(100);
}

void killCode(){
  // This function is an ISR to stop the process
  killState = HIGH;
}

void resetPulse(){
  // Sets the reset pin high for resetLength ms
  digitalWrite(resetPin, HIGH);
  delay(resetLength);
  digitalWrite(resetPin, LOW);
}

void backup(){
  // Changes the gate voltage back 5 steps in the middle
  // of the reset pulse.
  digitalWrite(resetPin, HIGH);
  delay(resetLength/2.0);
  gateV = gateV - 5*gate_step;
  write_value(gateV);
  delay(resetLength/2.0);
  digitalWrite(resetPin, LOW);
  
}

int isOpen(float sV){
  // Checks if the source voltage is within threshold
  // to be labelled as open
  return abs(sourceRest - sV) < vS_thresh;
}

int isClosed(float sV){
  // Checks if the source voltage is out of  threshold
  // to be labelled as closed
  return abs(sourceRest - sV) < vS_thresh;
}

int openNumTimesQ(){
  // Makes sure the switch is open numOC times in a row, quietly
  int numOpen = 0;
  while(numOpen < numOC){
    float sourceV = getSourceVolt();
    
    if( isOpen(sourceV) ){
      // then the device has opened!
      numOpen += 1;
    }

    else{
      numOpen = 0;
      return 0;
    }
  }
  return 1;
  
}

int openNumTimes(){
  // Makes sure switch is open unmOC times in a row, with details to the user
  int numOpen = 0;
  while(numOpen < numOC){
    float sourceV = getSourceVolt();
    
    if( isOpen(sourceV) ){
      // then the device has opened!
      Serial.print("Open at ");
      Serial.print(mapf(gateV,0,4095,0,5)*19.5);
      Serial.print(" V with ");
      Serial.print(sourceV);
      Serial.println(" V on source");
      numOpen += 1;
    }

    else{
      Serial.print("closed at ");
      Serial.print(numOpen);
      Serial.print(" while waiting for ");
      Serial.print(numOC);
      Serial.println(" cycles.");
      numOpen = 0;
      return 0;
    }
  }
  return 1;
}

void loop() {
  
  // Checks if process should be stopped
  if(killState == HIGH){
    if(printKill){
      Serial.println("stopped");
    }
    digitalWrite(ledPin, LOW);
    printKill = LOW;
    delay(1000);
  }

  // Wait for python code to say OK to run
  else if (Serial.available() > 0) {
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
      case 's':
        Serial.println("received s, stopping process");
        killState = HIGH;
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
        
      
        // check if should stop the process
        if( killState == HIGH ){
          write_value(0);
          contLoop = 0;
          Serial.println("state killed");
          digitalWrite(ledPin,LOW);
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


        // start ramp up
        Serial.println("start ramp up");
        int ru = rampUp();

        if(!ru){
          // something wrong happened, get out of loop
          Serial.println("ramp up failed");
          digitalWrite(ledPin, LOW);
          break;
        }
        else{

          // need to make sure that it's open for enough time
          Serial.println("start ramp down");
          
          // start ramp down
          int rd = rampDown();
          
          if(!rd){
            // something wrong happened, get out of loop
            Serial.println("ramp down failed");
            digitalWrite(ledPin, LOW);
          }


          Serial.print("The gate voltage is waiting at ");
          Serial.print(mapf(gateV,0,4095,0,5)*19.5);
          Serial.println(" V. Waiting for RF Ready (r).");

          // The switch has opened from the initial closure.
          // Need to wait to be ready for RF application.
          // If the switch is still noisy and closes beforehand, need
          // to backoff more.
          while(!rfReady){
            
            // check if should stop the process
            if( killState == HIGH ){
              write_value(0);
              contLoop = 0;
              Serial.println("state killed");
              digitalWrite(ledPin,LOW);
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
              if(inByte == 'r'){
                rfReady = 1;
                break;
              }
            }
            
            // check if need to ramp down
            if(!openNumTimesQ()){
              rampDown();
            }
          }

          float sourceV = getSourceVolt();

          Serial.print("The gate voltage is waiting at ");
          Serial.print(mapf(gateV,0,4095,0,5)*19.5);
          Serial.println(" V. Maintaining voltage and waiting for closure.");
          
          // wait until kill. just hold until the RF pulse happens
          while(1){

            sourceV = getSourceVolt();

            if( abs(sourceRest - sourceV) > vS_thresh ){
              // the switch has closed from RF or something else
              Serial.print("The switch closed with ");
              Serial.print(sourceV);
              Serial.println(" V on source. Applying reset pulse and setting gate voltage back 5 steps");
              backup();
              break;
            }
            
            // check if should stop
            // check if should stop the process of waiting for RF pulse
            if( killState == HIGH ){
              write_value(0);
              contLoop = 0;
              Serial.println("state killed");
              digitalWrite(ledPin,LOW);
              break;
            }
            
            // check if should continue loop of waiting for RF pulse
            if ( Serial.available() > 0 ) {
              inByte = Serial.read();
              // s will be sent in ctrl+c case
              if (inByte == 's') {
                write_value(0);
                contLoop = 0;
                break;
              }
            }
            delay(100);
          }
        }       
      

        // finished testing, now set output to 0 V
        write_value(0);
        digitalWrite(ledPin, LOW);
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
  if ( gateV > gate_limit){
    Serial.println(gateV - gate_limit);
    Serial.println(gateV);
    Serial.println(gate_limit);
    Serial.println("Open Switch");
    write_value(0);
    return 0;
  }

  // good to start the ramp up
  while( gateV < gate_limit ) {
    
    // check if should stop the process
    if( killState == HIGH){
      write_value(0);
      Serial.println("state killed in ramp up");
      digitalWrite(ledPin, LOW);
      return 0;
    }

    unsigned long currentMillis = millis();

    // only print out when it increases by a volt
    //prevV = gateV;

    // increase gate voltage
    if(currentMillis - previousMillis >= gate_delay){
      gateV += gate_step;
      write_value(gateV);
      previousMillis = currentMillis;
      //Serial.print("gate V orig: ");
      //Serial.println(utof(gateV),5);
      //if(gateV - prevV > 1){
        Serial.print("gate V final: ");
        Serial.println(utof(gateV)*19.5,5);
        //Serial.print("Binary: ");
        //Serial.println(gateV, BIN);
        //Serial.println();
      //}
      Serial.print("Source volt: ");
      Serial.println(sourceV);
      
    }
    
    // look at source voltage to see if switch
    sourceV = getSourceVolt();
    
    if( abs(sourceRest - sourceV) > vS_thresh ){
      // then the device has closed!
      Serial.print("Closed at ");
      Serial.print(mapf(gateV,0,4095,0,5)*19.5);
      Serial.print(" V with ");
      Serial.print(sourceV);
      Serial.println(" V on source");

      // don't want device to touch for a long time
      // so need to try to pull it off

      // apply reset pulse
      backup();
      
      
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

  if( openNumTimes() ){
    // the switch is open from the start
    Serial.print("Open from start of Ramp Down with ");
    Serial.print(sourceV);
    Serial.println(" V on source");
    return 1;
  }

  // check if out of bounds to ramp up
  if ( gateV < gate_step ){
    Serial.println("Not Opening");
    return 0;
  }

  // good to start the ramp down
  while( gateV > gate_step ) {
    
    // check if should stop the process
    if( killState == HIGH){
      write_value(0);
      Serial.println("state killed in ramp down");
      digitalWrite(ledPin, LOW);
      return 0;
    }

    unsigned long currentMillis = millis();
    
    // decrease gate voltage if time is correct
    if(currentMillis - previousMillis >= gate_delay){
      previousMillis = currentMillis;
      Serial.print("gate V final: ");
      Serial.println(utof(gateV)*19.5);
      
      gateV -= gate_step;
      write_value(gateV);
      Serial.print("Source volt: ");
      Serial.println(sourceV);
    }

    // look at source voltage to see if switch
    sourceV = getSourceVolt();

    // check if open for n times
    if( openNumTimes() ){
      // then the device has opened!
      Serial.print("Opened at ");
      Serial.print(mapf(gateV,0,4095,0,5)*19.5);
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

void write_value(uint16_t value) {
  // This function will write a value to the MCP49221E DAC
  // channel (0 = DACA, 1 = DACB) // Vref input buffer (0 = unbuffered, 1 = buffered) // gain (1 = 1x, 0 = 2x)  // Output power down power down (0 = output buffer disabled) //  12 bits of data
  uint16_t out = (0 << 15) | (1 << 14) | (1 << 13) | (1 << 12) | (value);
  digitalWrite(slaveSelectPin, LOW);
  SPI.transfer(out >> 8);         //you can only put out one byte at a time so this is splitting the 16 bit value.
  SPI.transfer(out & 0xFF);
  digitalWrite(slaveSelectPin, HIGH);
}
