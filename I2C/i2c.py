import csv
import logging
from smbus2 import SMBus, i2c_msg
import time
import pandas as pd
from datetime import datetime
import struct

logging.basicConfig(filename='pruebai2c.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

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
        print(values)
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

alpha = [3.24892489, 4.324242, 5.432432]
beta = [-0.3427482, -0.5347832, -0.1123314]
while True:
    data = read_data()
    if data is not None:
        print("Data Recivied")
        save_to_csv(data,filename)
        send_data(alpha,beta)
    time.sleep(5)
