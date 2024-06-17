#include <Arduino.h>
#include <Arduino_CRC32.h>

void enviarDatos(const int data[], int dataSize) {
  // Calcular CRC32 para los datos
  CRC32 crc;
  for (int i = 0; i < dataSize; i++) {
    crc.update(data[i]);
  }
  uint32_t crcValue = crc.finalize();

  // Enviar el tamaño de la lista primero
  Serial1.print("SIZE:");
  Serial1.println(dataSize);

  // Enviar los elementos de la lista
  for (int i = 0; i < dataSize; i++) {
    Serial1.print("DATA:");
    Serial1.println(data[i]);
  }

  // Enviar el CRC32
  Serial1.print("CRC:");
  Serial1.println(crcValue);
}

bool recibirDatos(double receivedList[], int &receivedSize) {
  if (Serial1.available()) {
    String receivedData = Serial1.readStringUntil('\n');
    if (receivedData.startsWith("SIZE:")) {
      receivedSize = receivedData.substring(5).toInt();

      for (int i = 0; i < receivedSize; i++) {
        while (!Serial1.available()) {
          // Esperar hasta que se reciba el siguiente dato
        }
        String dataString = Serial1.readStringUntil('\n');
        if (dataString.startsWith("DATA:")) {
          receivedList[i] = dataString.substring(5).toDouble();
        }
      }

      // Recibir y verificar CRC32
      while (!Serial1.available()) {
        // Esperar hasta que se reciba el CRC
      }
      String crcString = Serial1.readStringUntil('\n');
      if (crcString.startsWith("CRC:")) {
        uint32_t received_crc = crcString.substring(4).toInt();
        
        CRC32 crc;
        for (int i = 0; i < receivedSize; i++) {
          crc.update((uint8_t*)&receivedList[i], sizeof(receivedList[i]));
        }
        uint32_t calculated_crc = crc.finalize();

        if (calculated_crc != received_crc) {
          Serial.println("Error: CRC32 no coincide");
          return false;
        }
      }

      // Imprimir la lista recibida para depuración
      Serial.print("Lista recibida: ");
      for (int i = 0; i < receivedSize; i++) {
        Serial.print(receivedList[i], 10);
        if (i < receivedSize - 1) {
          Serial.print(", ");
        }
      }
      Serial.println();
      return true;
    }
  }
  return false;
}

int humedades[6] = {1845, 3948, 7483, 10473, 15034, 18653};
void setup() {
  Serial.begin(9600); // Serial Arduino
  Serial.println("Listo");
  Serial1.begin(9600); // Serial Raspberry Pi
}

void loop() {
  double receivedList[12]; // Ajustar tamaño según sea necesario

  int receivedSize = 0;

  if (recibirDatos(receivedList, receivedSize)) {
    enviarDatos(humedades, 6);
  }

  delay(1000); // Esperar un segundo antes de recibir nuevamente
}

