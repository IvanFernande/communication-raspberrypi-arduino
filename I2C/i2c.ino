#include <Wire.h>

// Define the I2C slave address
#define SLAVE_ADDRESS 0x6b

// Array to store the data to be sent
uint8_t number[14] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
// Variable to store a received number
int number2;
// Array to store sensor values and a quality check value
int values[7] = {5096, 10000, 8000, 15000, 20000, 7586, 23456};
// Constants for the number of doubles to be received
const int NUM_DOUBLES_ALPHA = 3; 
const int NUM_DOUBLES_BETA = 3; 
const int TOTAL_DOUBLES = NUM_DOUBLES_ALPHA + NUM_DOUBLES_BETA + 1; 

void setup() {
  Serial.begin(9600);  // Initialize serial communication
  Wire.begin(SLAVE_ADDRESS);  // Join I2C bus as slave
  Wire.onReceive(receiveData);  // Register function to handle data reception
  Wire.onRequest(sendData);  // Register function to handle data requests

  Serial.println("Ready!");
}

void loop() {
  delay(100);  // Small delay in the main loop
}

// Function to handle data reception over I2C
void receiveData(int byteCount) {
  // Array to store received data as doubles
  double receivedData[TOTAL_DOUBLES];
  // Buffer to store raw byte data
  byte buffer[sizeof(double) * TOTAL_DOUBLES];
  
  int index = 0;
  // Read data from I2C bus into the buffer
  while (Wire.available() && index < sizeof(buffer)) {
    buffer[index++] = Wire.read();
  }

  // If the received data size matches the expected size
  if (index == sizeof(buffer)) {
    // Convert raw bytes to doubles
    for (int i = 0; i < TOTAL_DOUBLES; i++) {
      memcpy(&receivedData[i], &buffer[i * sizeof(double)], sizeof(double));
    }

    // Print the alpha list
    Serial.println("Alpha list:");
    for (int i = 0; i < NUM_DOUBLES_ALPHA; i++) {
      Serial.print("Received double: ");
      Serial.println(receivedData[i], 8);
    }

    // Print the beta list
    Serial.println("Beta list:");
    for (int i = NUM_DOUBLES_ALPHA; i < NUM_DOUBLES_ALPHA + NUM_DOUBLES_BETA; i++) {
      Serial.print("Received double: ");
      Serial.println(receivedData[i], 8);
    }

    // Print the check value
    Serial.println("Check value:");
    Serial.print("Received double: ");
    Serial.println(receivedData[NUM_DOUBLES_ALPHA + NUM_DOUBLES_BETA], 8);
    
  } else {
    // Print an error message if data size mismatch
    Serial.println("Error: Received data size mismatch");
  }
}

// Function to handle data requests over I2C
void sendData() {
  // Convert sensor values to high and low bytes
  for (int i = 0; i < 7; i++) {
    int highByte = (values[i] >> 8) & 0xFF;
    int lowByte = values[i] & 0xFF;
    number[i * 2] = highByte;
    number[i * 2 + 1] = lowByte;
  }

  // Print the values being sent
  Serial.print("Sending values: ");
  for (int i = 0; i < 7; i++) {
    Serial.print(values[i]);
    if (i < 6) {
      Serial.print(", ");
    }
  }
  Serial.println();
  
  // Send the data over I2C
  Wire.write(number, sizeof(number));
}
