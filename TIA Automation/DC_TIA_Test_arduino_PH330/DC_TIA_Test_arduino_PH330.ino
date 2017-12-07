    // This file controls an Arduino Due to test an 
    // NZERO NEMS Switch with the DC-TIA test.
    
    // Leanna Pancoast 9 Nov 2017
    
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
      SPI.setClockDivider(SPI_CLOCK_DIV2); // 24 MHz on Teensy
    
      Serial.println("Ready");
    
      pinMode(13, OUTPUT);
      write_value(0);
    
      delay(100);
    }
    
    void loop() {
      // Wait for python code to say OK to run
      if (Serial.available() > 0){
        // get incoming byte:
        inByte = Serial.read();
    
        switch (inByte){
          case 'p':
            delay(10);
            // Parameters are being input
            // Gate start, gate step, gate end
            if(Serial.available() > 0){
              gate_start = Serial.read();
            }
            if(Serial.available() > 0){
              gate_step = Serial.read();
            }
            if(Serial.available() > 0){
              gate_limit = Serial.read();
            }
            Serial.println("received parameters");
            break;
          case 'b':
            // Begin the sweep
            int worked = 1;
            float vG = gate_start;
            int vS = analogRead(sourcePin);
            // map to get real voltage number
            float vSa = mapf(vS, 0, 1023, 0, 5);
            
            // check if switch already closed at beginning
            if( abs(2.8 - vSa) > vS_thresh){
              Serial.println("Shorted from the start");
              Serial.println(vSa);
              worked = 0;
            }

            int contLoop = 1;
            // can begin the sweep
            //Serial.print("2.8 - vsa = ");
            //Serial.println(2.8-vSa);
            //Serial.println(2.8-vSa > vS_thresh);
            while (contLoop == 1 && abs(2.8 - vSa) < vS_thresh){
              if(Serial.available() > 0){
                inByte = Serial.read();
                if(inByte == 's'){
                  write_value(0);
                  contLoop = 0;
                }
              }
              delay(500);
              
              if( vG - gate_limit > 0){
                // open switch
                Serial.println("open switch");
                worked = 0;
                break;
              }
    
              // Tell PC still in loop
              Serial.println("loop");
    
              // Tell PC the gate voltage
              //Serial.println('g');
              
              // increase bias
              vG += gate_step;
              Serial.println(vG);
              
              // set bias voltage
              //vGa = vG / 20.0; // there will be 20x gain, only need to
              // output 1/20 of desired value from Due
              
              
              write_value(floor(mapf(vG, 0, 5, 0, 4095)));
              delay(5);
    
              // read the source voltage
              vS = analogRead(sourcePin);
              vSa = mapf(vS,0, 1023, 0, 5);
              // Tell PC the TIA voltage
              Serial.print("s: ");
              Serial.println(vSa);              
            }
    
          // exited loop, now set output to 0 V
          write_value(0);
          
          if(worked){
            // tell PC that it worked and at what voltage
            Serial.println("worked");
            Serial.println(vG);
            Serial.println(vSa);
          }
        }
      }
    }
    
    void write_value(float value){
      // channel (0 = DACA, 1 = DACB) // Vref input buffer (0 = unbuffered, 1 = buffered) // gain (1 = 1x, 0 = 2x)  // Output power down power down (0 = output buffer disabled) //  12 bits of data
      value = value/20;
      //Serial.print("value: ");
      //Serial.println(value);
      int v = value;
      //Serial.print("v: ");
      //Serial.println(v);
      uint16_t out = (0<<15) | (1<<14) | (1<<13) | (1<<12) | (v);
      digitalWrite(slaveSelectPin, LOW);
      //Serial.print("out: ");
      //Serial.println(out);
      SPI.transfer(out >> 8);         //you can only put out one byte at a time so this is splitting the 16 bit value.
      SPI.transfer(out & 0xFF);
      digitalWrite(slaveSelectPin, HIGH);
    }
