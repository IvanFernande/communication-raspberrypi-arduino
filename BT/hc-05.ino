void setup() {
  Serial.begin(9600); // Serial Arduino
  Serial.println("Listo"); 
  Serial1.begin(9600); // Serial Raspberry Pi

}

void loop() {
  if (Serial1.available()){
    Serial.write(Serial1.read());
  }

  if (Serial.available()){
    Serial1.write(Serial.read());
  }
}
