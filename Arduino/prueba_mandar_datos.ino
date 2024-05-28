#include <Wire.h>

#define SLAVE_ADDRESS 0x6b

uint8_t number[12] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
int number2;
int values[6] = {5096, 10000, 8000, 15000, 20000, 7586};

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
    number2 = Wire.read();
    Serial.print("data received: ");
    Serial.println(number2);
  }
}

void sendData() {
  for (int i = 0; i < 6; i++) {
    int highByte = (values[i] >> 8) & 0xFF;
    int lowByte = values[i] & 0xFF;
    number[i * 2] = highByte;
    number[i * 2 + 1] = lowByte;
  }

  Serial.print("Sending values: ");
  for (int i = 0; i < 6; i++) {
    Serial.print(values[i]);
    if (i < 5) {
      Serial.print(", ");
    }
  }
  Serial.println();
  
  Wire.write(number, sizeof(number));
}