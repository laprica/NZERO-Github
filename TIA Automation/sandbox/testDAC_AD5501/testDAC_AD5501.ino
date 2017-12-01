// Test output to AD5501, a 12 bit DAC (up to 60 V) with SPI

// Voltage will step up (or down) every 100 ms.
// Unless the ramp is commented out, then it will hold
// a constant voltage.


// Thanks to equaliser for a test ze used with a Teensy
// and uploaded to GitHub.
// https://gist.github.com/equaliser/8216031

// Leanna Pancoast 9 Nov 2017

/*
 * Circuit:
 * AD5501 DAC on the evaluation board
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
  Serial.begin(9600);

  pinMode(slaveSelectPin, OUTPUT);
  
  SPI.beginTransaction(SPISettings(8000000,LSBFIRST,SPI_MODE0));
  SPI.begin();

  delay(100);

  read_control_reg();
  while(1){
    Serial.println("waiting");
    if(Serial.available() > 0){
      turn_DAC_channel_on();
      write_nop();
      Serial.println("starting");
      break;
    }
    delay(500);
  }
  read_control_reg();

}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println(mapf(i,0,4095,0,30));
  i +=10;
  write_value(i);
  read_control_reg();
  delay(500);
  if(i > 4095) {
    i = 0;
  }
}

void read_control_reg(){
  // R/Wb bit // 111 to write to control register // DB11 - DB7 is 0 // DB2 DAC channel (0 = off, 1 = on)
  uint16_t out = (1<<15) | (1<<14) | (1<<13) | (1<<12) | (0<<2);
  uint16_t in = 0;
  uint16_t in2 = 0;
  Serial.print("Reading: ");
  Serial.println(out);
  digitalWrite(slaveSelectPin, LOW);
  in = SPI.transfer(out >> 8);         //you can only put out one byte at a time so this is splitting the 16 bit value.
  in2 = SPI.transfer(0x00);
  digitalWrite(slaveSelectPin, HIGH);
  Serial.print("received: ");
  Serial.println(in);
  Serial.println(in2);
}

void turn_DAC_channel_on(){
  // R/Wb bit // 111 to write to control register // DB11 - DB7 is 0 // DB2 DAC channel (0 = off, 1 = on)
  uint16_t out = (0<<15) | (1<<14) | (1<<13) | (1<<12) | (1<<2);
  Serial.print("Turn DAC on writing control: ");
  Serial.println(out);
  digitalWrite(slaveSelectPin, LOW);
  SPI.transfer16(out);         //you can only put out one byte at a time so this is splitting the 16 bit value.
  digitalWrite(slaveSelectPin, HIGH);
}

void write_nop(){
  // R/Wb bit // 000 for nop// DB11 - DB7 is 0 // DB2 DAC channel (0 = off, 1 = on)
  uint16_t out = (0<<15) | (0<<14) | (0<<13) | (0<<12) | (1<<2);
  digitalWrite(slaveSelectPin, LOW);
  SPI.transfer16(out);
  digitalWrite(slaveSelectPin, HIGH);
}

void turn_DAC_channel_off(){
  // R/Wb bit // 111 to write to control register // DB11 - DB7 is 0 // DB2 DAC channel (0 = off, 1 = on)
  uint16_t out = (0<<15) | (1<<14) | (1<<13) | (1<<12) | (0<<2);
  digitalWrite(slaveSelectPin, LOW);
  SPI.transfer(out >> 8);         //you can only put out one byte at a time so this is splitting the 16 bit value.
  SPI.transfer(out & 0xFF);
  digitalWrite(slaveSelectPin, HIGH);
}

void write_value(int value){
  // R/Wb bit (0 = write, 1 = read) // A2,A1,A0 = 0,0,1 to write to DAC input register //  12 bits of data MSB first
  uint16_t out = (0<<15) | (0<<14) | (0<<13) | (1<<12) | (164);
  digitalWrite(slaveSelectPin, LOW);
  Serial.print("writing: ");
  Serial.println(out);
  SPI.transfer16(out);         //you can only put out one byte at a time so this is splitting the 16 bit value.
  //SPI.transfer(out & 0xFF);
  digitalWrite(slaveSelectPin, HIGH);
}

