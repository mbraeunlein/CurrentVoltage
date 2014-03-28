
// the setup routine runs once when you press reset:
void setup() {
  analogReadResolution(12);  

  // initialize serial communication at 9600 bits per second:
  SerialUSB.begin(115200);
}

// the loop routine runs over and over again forever:
void loop() {
  //double totalVoltage = 4.1;
  uint16_t sensorValue = analogRead(A0);
  SerialUSB.println(sensorValue);
//  SerialUSB.write(highByte(sensorValue));
//  SerialUSB.write(lowByte(sensorValue));

  //  oldValue = sensorValue;
}

