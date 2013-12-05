int oldValue = 0;

// Define various ADC prescaler
const unsigned char PS_16 = (1 << ADPS2);
const unsigned char PS_32 = (1 << ADPS2) | (1 << ADPS0);
const unsigned char PS_64 = (1 << ADPS2) | (1 << ADPS1);
const unsigned char PS_128 = (1 << ADPS2) | (1 << ADPS1) | (1 << ADPS0);
 
// the setup routine runs once when you press reset:
void setup() {
  analogReference(INTERNAL);
  
  // initialize serial communication at 9600 bits per second:
  Serial.begin(115200);
  
  // set up the ADC
  ADCSRA &= ~PS_128;  // remove bits set by Arduino library
  
  // you can choose a prescaler from above.
  // PS_16, PS_32, PS_64 or PS_128
  ADCSRA |= PS_16;    // set our own prescaler to 128 
}

// the loop routine runs over and over again forever:
void loop() {
  //double totalVoltage = 4.1;
  int sensorValue = analogRead(A0);
  Serial.println(sensorValue);
  
//  oldValue = sensorValue;
}
