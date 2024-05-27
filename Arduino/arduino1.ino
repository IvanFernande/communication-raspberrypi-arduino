#include <Wire.h>

#define SLAVE_ADDRESS 0x6b

int number = 0;

void setup() {
  Serial.begin(9600);
  Wire.begin(SLAVE_ADDRESS);
  Wire.onReceive(receiveData);
  Wire.onRequest(sendData);

  Serial.println("Ready!");
}

void loop() {
  delay(100);
}

void receiveData(int byteCount) {
  Serial.println("receiveData");
  while (Wire.available()) {
    number = Wire.read();
    Serial.print("data received: ");
    Serial.println(number);
  }
}

void sendData() {
  number = number + 1;
  Wire.write(number);
}
