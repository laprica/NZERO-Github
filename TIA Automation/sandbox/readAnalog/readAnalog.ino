void setup() {
  Serial.begin(9600);

}

float mapf(float x, float in_min, float in_max, float out_min, float out_max){
  return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;
}

void loop() {
  // put your main code here, to run repeatedly:
  Serial.println(mapf(analogRead(A0),0,1023,0,5));

}
