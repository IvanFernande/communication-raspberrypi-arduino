void setup() {
  Serial.begin(9600); // Initialize serial communication for Arduino at 9600 baud
  Serial.println("Ready"); 
  Serial1.begin(9600); // Initialize serial communication for Raspberry Pi at 9600 baud
}

void loop() {
  // Check if there is data available to read from the Raspberry Pi
  if (Serial1.available()) {
    Serial.write(Serial1.read()); // Read the data from Serial1 and write it to the Serial (Arduino)
  }

  // Check if there is data available to read from the Arduino
  if (Serial.available()) {
    Serial1.write(Serial.read()); // Read the data from Serial (Arduino) and write it to Serial1 (Raspberry Pi)
  }
}
