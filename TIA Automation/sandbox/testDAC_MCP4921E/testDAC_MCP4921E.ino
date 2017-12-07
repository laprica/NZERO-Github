// Test output to MCP4921E, a 12 bit DAC with SPI

// Voltage will step up (or down) every 100 ms.
// Unless the ramp is commented out, then it will hold
// a constant voltage.


// Thanks to equaliser for a test ze used with a Teensy
// and uploaded to GitHub.
// https://gist.github.com/equaliser/8216031

// Leanna Pancoast 9 Nov 2017

/*
 * Circuit:
 * MCP4921E DAC
 */

// need to include SPI library
#include <SPI.h>

int slaveSelectPin = 10;
int i = 0;

float mapf(float x, float in_min, float in_max, float out_min, float out_max){
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  pinMode(slaveSelectPin, OUTPUT);
  
  //SPI.begin();
  //SPI.setClockDivider(SPI_CLOCK_DIV2); // 24 MHz

  SPI.beginTransaction(SPISettings(4000000,MSBFIRST,SPI_MODE0));
  SPI.begin();
  
  delay(100);

}

void loop() {
  // put your main code here, to run repeatedly:
  mapf(i,0,4095,0,5);
  //Serial.println(mapf(i,0,4095,0,5));
  i +=1;
  write_value(i);
  //delay(500);
  if(i > 1200) {
    i = 0;
  }
}

void write_value(int value){
  // channel (0 = DACA, 1 = DACB) // Vref input buffer (0 = unbuffered, 1 = buffered) // gain (1 = 1x, 0 = 2x)  // Output power down power down (0 = output buffer disabled) //  12 bits of data
  uint16_t out = (0<<15) | (1<<14) | (1<<13) | (1<<12) | (value);
  digitalWrite(slaveSelectPin, LOW);
  SPI.transfer(out >> 8);         //you can only put out one byte at a time so this is splitting the 16 bit value.
  SPI.transfer(out & 0xFF);
  digitalWrite(slaveSelectPin, HIGH);
}

