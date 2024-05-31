# Import de librerias
import csv
import logging
from smbus2 import SMBus, i2c_msg
import time
import pandas as pd
from datetime import datetime, timedelta
import struct
import subprocess

# Scripts:
### checksat: comprueba que durante un dia si ha habido saturación o no.
### execute_nn: recorta los datos para hallar el fin de saturacion y consigue valores de alpha y beta.

logging.basicConfig(filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

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
def send_data(float1, float2):
    try:
        alpha_ard = struct.pack('d',float1)
        beta_ard = struct.pack('d',float2)
        sleep_permiso_ard = struct.pack('d',0.2000)
        print(len(alpha_ard + beta_ard + sleep_permiso_ard))
        feedback = i2c_msg.write(DEVICE_ADDRESS, alpha_ard + beta_ard + sleep_permiso_ard)
        bus.i2c_rdwr(feedback)

        logging.info(f'Data enviada al Arduino: {float1}, {float2}')

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

alpha = 12.47483473
beta = -12.45357439
formato = "%H:%M:%S"
fecha_ref1 = "01:00:00"
fecha_ref2 = "01:30:00"
checksat_ab = False

while True:
    data = read_data()
    if data is not None:
        save_to_csv(data,filename)
        send_data(alpha,beta)
    time.sleep(5)
    try:
        fecha_actual = datetime.strptime(str(datetime.now())[11:19],formato)
        logging.info("Fecha formateada con exito")
        if fecha_ref1 < fecha_actual < fecha_ref2:
            logging.info(f"Fecha actual entre las {fecha_ref1} y {fecha_ref2}")
            try:
                logging.info("Se ejecutará checksat.py")
                output_checksat = subprocess.run(['python','checksat.py'], capture_output=True, text=True)
            except Exception as e:
                logging.error(f"Mientras se intentaba ejecutar checksat.py ocurrio: {e}")
    except Exception as e:
        logging.error(f"Error al formatear la fecha: {e}")


