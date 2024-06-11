# Import de librerias
import csv
import serial
import logging
import time
import pandas as pd
from datetime import datetime, timedelta
import subprocess
import re

# Scripts:
### checksat: comprueba que durante un dia si ha habido saturación o no.
### execute_nn: recorta los datos para hallar el fin de saturacion y consigue valores de alpha y beta.

logging.basicConfig(filename='app_bt.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

ser = serial.Serial(
    '/dev/rfcomm0',
    9600,
    timeout=1
)

filename = "historial_datos_bt.csv"
column_names = ["DateTime", "Sensor 0", "Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4", "Sensor 5"]

try:
    pd.read_csv(filename)
except FileNotFoundError:
    df = pd.DataFrame(columns=column_names)
    df.to_csv(filename, index=False)

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
                            receivedData.append(float(dataLine.split(":")[1]))
                            break

            return receivedData
    return None
  def enviar_datos(ser, lista_datos):
    # Enviar el tamaño de la lista primero
    ser.write(f'SIZE:{len(lista_datos)}\n'.encode('utf-8'))

    # Enviar los elementos de la lista
    for dato in lista_datos:
        ser.write(f'DATA:{dato}\n'.encode('utf-8'))


def save_to_csv(values, filename):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        data = {
            "Timestamp": [timestamp],
            "Value1": [values[0]],
            "Value2": [values[1]],
            "Value3": [values[2]],
            "Value4": [values[3]],
            "Value5": [values[4]],
            "Value6": [values[5]],
        }

        df = pd.DataFrame(data)

        df.to_csv(filename, mode='a', index=False, header=False)
        logging.info(f"Data saved to {filename}: {values}")
    except Exception as e:
        logging.error(f"Error saving data to {filename}: {e}")

output_red = [1.0000, 1.00000, 1.0000, 0.0000, 0.0000, 0.0000]  # Valores de alpha y beta juntos
formato = "%H:%M:%S"
fecha_ref1 = datetime.strptime("13:15:00", formato)
fecha_ref2 = datetime.strptime("13:30:00", formato)
checksat_ab = True

while True:
    data = recibir_datos(ser)
    if data is not None:
        save_to_csv(data,filename)
    enviar_datos(ser, output_red)
    print("Datos enviados", output_red)
    time.sleep(5)
    try:
        fecha_actual = datetime.strptime(str(datetime.now())[11:19],formato)
        logging.info("Fecha formateada con exito")
        if fecha_ref1 < fecha_actual < fecha_ref2 and checksat_ab:
            checksat_ab = False
            logging.info(f"Fecha actual entre las {fecha_ref1} y {fecha_ref2}")
            try:
                logging.info("Se ejecutará checksat.py")
                output_checksat = subprocess.run(['python','checksat.py'], capture_output=True, text=True)
                logging.info('Ejecución de temporizador.py completada con código de retorno: %s', output_checksat.returncode)
                logging.info('Salida estándar de temporizador.py: %s', output_checksat.stdout)
                logging.info('Salida de error de temporizador.py: %s', output_checksat.stderr)
            except Exception as e:
                logging.error(f"Mientras se intentaba ejecutar checksat.py ocurrio: {e}")

            output_checksat = output_checksat.stdout.strip()

            if output_checksat == "corregir":
                logging.info('Condicion "corregir" satisfecha, ejecutando la red neuronal')

                try:
                    output_execute_nn = subprocess.run(['python','execute_nn.py'], capture_output=True, text=True)
                    logging.info('Ejecución de codigo_servidor.py completada con código de retorno: %s', output_execute_nn.returncode)
                    logging.info('Salida estándar de codigo_servidor.py: %s', output_execute_nn.stdout)
                    logging.info('Salida de error de codigo_servidor.py: %s', output_execute_nn.stderr)

                except Exception as e:
                    logging.error(f'Mientras se intentaba ejecutar la red neuronal ocurrio: {e}')

                output_execute_nn = output_execute_nn.stdout
                print(output_execute_nn)

                patron_alpha = r"Alpha: \[([0-9.\s-]+)\]"
                patron_beta = r"Beta: \[([0-9.\s-]+)\]"
                alpha_match = re.search(patron_alpha, output_execute_nn)
                beta_match = re.search(patron_beta, output_execute_nn)

                if alpha_match and beta_match:

                    alpha = list(map(float, alpha_match.group(1).split()))
                    beta = list(map(float, beta_match.group(1).split()))
                    logging.info("alpha: %s", alpha)
                    logging.info("beta: %s", beta)
                    print("alpha:", alpha)
                    print("beta:", beta)
                    output_red = alpha + beta

                else:
                    logging.warning("No se encontraron las listas Alpha y Beta en la cadena.")
                    print("No se encontraron las listas Alpha y Beta en la cadena.")
        elif fecha_actual > fecha_ref2:
            checksat_ab = True

    except Exception as e:
        logging.error(f"Error al formatear la fecha: {e}")
