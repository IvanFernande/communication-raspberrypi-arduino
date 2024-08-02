#include <Arduino.h>

// Function to send data array to Serial1
void enviarDatos(const int data[], int dataSize) {
  // Send the size of the list first
  Serial1.print("SIZE:");
  Serial1.println(dataSize);

  // Send the elements of the list
  for (int i = 0; i < dataSize; i++) {
    Serial1.print("DATA:");
    Serial1.println(data[i]);
  }
}

// Function to receive data from Serial1
bool recibirDatos(double receivedList[], int &receivedSize) {
  if (Serial1.available()) {
    String receivedData = Serial1.readStringUntil('\n');  // Read data until newline character
    if (receivedData.startsWith("SIZE:")) {
      receivedSize = receivedData.substring(5).toInt();  // Extract and convert the size
      
      // Loop to read each data element based on received size
      for (int i = 0; i < receivedSize; i++) {
        while (!Serial1.available()) {
          // Wait until data is available
        }
        String dataString = Serial1.readStringUntil('\n');  // Read data until newline character
        if (dataString.startsWith("DATA:")) {
          receivedList[i] = dataString.substring(5).toDouble();  // Extract and convert the data
        }
      }

      // Print the received list for debugging
      Serial.print("Received list: ");
      for (int i = 0; i < receivedSize; i++) {
        Serial.print(receivedList[i], 10);  // Print each element with 10 decimal places
        if (i < receivedSize - 1) {
          Serial.print(", ");
        }
      }
      Serial.println();
      return true;  // Return true indicating data was received successfully
    }
  }
  return false;  // Return false if no data was received
}

// Array of humidity values to send
int humedades[6] = {1845, 3948, 7483, 10473, 15034, 18653};

void setup() {
  Serial.begin(9600);  // Initialize serial communication for Arduino
  Serial.println("Ready");
  Serial1.begin(9600);  // Initialize serial communication for Raspberry Pi
}

void loop() {
  double receivedList[12];  // Adjust size as needed

  int receivedSize = 0;  // Variable to store the size of received list

  // Check if data was received and send data if so
  if (recibirDatos(receivedList, receivedSize)) {
    enviarDatos(humedades, 6);
  }

  delay(1000);  // Wait one second before receiving again
}

