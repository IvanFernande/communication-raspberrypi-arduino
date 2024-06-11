import serial
import csv
import time
import logging
import pandas as pd
from datetime import datetime

# Configura el logging
logging.basicConfig(level=logging.INFO)

def enviar_datos(ser, lista_datos):
    # Enviar el tamaño de la lista primero
    ser.write(f'SIZE:{len(lista_datos)}\n'.encode('utf-8'))

    # Enviar los elementos de la lista
    for dato in lista_datos:
        ser.write(f'DATA:{dato}\n'.encode('utf-8'))

def recibir_datos(ser):
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').strip()

        if line.startswith("SIZE:"):
            dataSize = int(line.split(":")[1])
            receivedData = []

            for _ in range(dataSize):
                while True:
                    if ser.in_waiting > 0:
                        dataLine = ser.readline().decode('utf-8').strip()
                        if dataLine.startswith("DATA:"):
                            receivedData.append(int(dataLine.split(":")[1]))
                            break

            return receivedData
    return None

def save_to_csv(values, filename):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data = {
            "DateTime": [timestamp],
            "Sensor 0": [values[0]],
            "Sensor 1": [values[1]],
            "Sensor 2": [values[2]],
            "Sensor 3": [values[3]],
            "Sensor 4": [values[4]],
            "Sensor 5": [values[5]],
        }
        df = pd.DataFrame(data)

        df.to_csv(filename, mode='a', index=False, header=False)
        logging.info(f"Data saved to {filename}: {values}")
    except Exception as e:
        logging.error(f"Error saving data to {filename}: {e}")

def main():
    filename = "historial_datos_bt.csv"
    column_names = ["DateTime", "Sensor 0", "Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4", "Sensor 5"]
    try:
        pd.read_csv(filename)
    except FileNotFoundError:
        df = pd.DataFrame(columns=column_names)
        df.to_csv(filename, index=False)

    # Configura la conexión serial
    ser = serial.Serial('/dev/rfcomm0', 9600)  # Reemplaza '/dev/ttyUSB0' por el puerto correcto
    time.sleep(2)  # Esperar un poco para asegurarse de que la conexión esté establecida

    lista_datos_a_enviar = [10, 20, 30, 40, 50, 60]  # Ejemplo de datos a enviar

    while True:
        # Enviar datos al Arduino
        enviar_datos(ser, lista_datos_a_enviar)

        # Esperar una respuesta del Arduino
        datos_recibidos = recibir_datos(ser)
        if datos_recibidos:
            save_to_csv(datos_recibidos, filename)

        time.sleep(5)  # Esperar un tiempo antes de volver a enviar datos

if __name__ == "__main__":
    main()
