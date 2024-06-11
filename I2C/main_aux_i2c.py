# Import de librerias
import csv
import logging
from smbus2 import SMBus, i2c_msg
import time
import pandas as pd
from datetime import datetime, timedelta
import struct
import subprocess
import re

# Scripts:
### checksat: comprueba que durante un dia si ha habido saturación o no.
### execute_nn: recorta los datos para hallar el fin de saturacion y consigue valores de alpha y beta.

logging.basicConfig(filename='app_i2c.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

DEVICE_ADDRESS = 0x6b

bus = SMBus(1)

filename = "historial_datos.csv"

column_names = ["DateTime", "Sensor 0", "Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4", "Sensor 5"]

try:
    pd.read_csv(filename)
except FileNotFoundError:
    df = pd.DataFrame(columns=column_names)
    df.to_csv(filename, index=False)

def read_data():
    try:
        msg = i2c_msg.read(DEVICE_ADDRESS, 14)
        bus.i2c_rdwr(msg)

        data = list(msg)
        values = []
        for i in range(0, 14, 2):
            value = (data[i] << 8) + data[i + 1]
            values.append(value)
        if 65535 in values:
            time.sleep(1)
            logging.info(f"Los valores recibidos han sido 65535")
            return None
        if values[-1] != 23456:
            time.sleep(1)
            logging.info(f"El valor de calidad no fue correcto")
            return None
        print("Dato recibido ", values)
              logging.info(f"Data read successfully: {values}")
        values.pop(-1)
        return values
    except Exception as e:
        logging.error(f"Error reading data: {e}")
        return None

def send_data(alpha_list, beta_list):
    try:
        packed_alpha = b''.join(struct.pack('d', num) for num in alpha_list)
        packed_beta = b''.join(struct.pack('d', num) for num in beta_list)
        sleep_permiso_ard = struct.pack('d',0.2000)

        packed_data = packed_alpha + packed_beta + sleep_permiso_ard
        print(len(packed_data))

        feedback = i2c_msg.write(DEVICE_ADDRESS, packed_data)
        bus.i2c_rdwr(feedback)

        logging.info(f'Data enviada al Arduino: {alpha_list}, {beta_list}')

    except Exception as e:
        logging.error(f"Error sending data to Arduino: {e}")

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

alpha = [1.0000, 1.00000, 1.0000]
beta = [0.000, 0.000, 0.000]
formato = "%H:%M:%S"
fecha_ref1 = datetime.strptime("12:00:00", formato)
fecha_ref2 = datetime.strptime("13:30:00", formato)
checksat_ab = True

while True:
    data = read_data()
    if data is not None:
        save_to_csv(data,filename)
        send_data(alpha,beta)
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

                else:
                    logging.warning("No se encontraron las listas Alpha y Beta en la cadena.")
                    print("No se encontraron las listas Alpha y Beta en la cadena.")
        elif fecha_actual > fecha_ref2:
            checksat_ab = True

    except Exception as e:
        logging.error(f"Error al formatear la fecha: {e}")


