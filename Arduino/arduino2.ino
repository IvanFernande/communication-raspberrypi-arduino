#include <Wire.h>

const byte I2C_ADDRESS = 0x08;
int receivedNumber = 0;
int numberToSend = 0;

void setup() {
  Wire.begin(I2C_ADDRESS);
  Wire.onReceive(receiveEvent);
  Wire.onRequest(requestEvent);
  Serial.begin(9600);
  while (!Serial);
  Serial.println("Arduino listo para comunicarse");
}

void loop() {
  // El Arduino espera por eventos I2C
  delay(100);
}

void receiveEvent(int howMany) {
  while (Wire.available()) {
    receivedNumber = Wire.read();
    Serial.print("Arduino recibió: ");
    Serial.println(receivedNumber);
  }
  numberToSend = receivedNumber + 1; // Por ejemplo, incrementar el numero recibido
}

void requestEvent() {
  Wire.write(numberToSend);
  Serial.print("Arduino envió: ");
  Serial.println(numberToSend);
}
