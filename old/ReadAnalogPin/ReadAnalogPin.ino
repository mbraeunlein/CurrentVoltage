void setup() {
  // put your setup code here, to run once:
  SerialUSB.begin(115200);
  analogReadResolution(12);
}

void loop() {
  // put your main code here, to run repeatedly: 
  SerialUSB.println(analogRead(A0));
}
