import zlib
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
        msg = i2c_msg.read(DEVICE_ADDRESS, 16)  # Leer 16 bytes en lugar de 14
        bus.i2c_rdwr(msg)

        data = list(msg)
        values = []
        for i in range(0, 12, 2):  # Leer solo los primeros 12 bytes como valores
            value = (data[i] << 8) + data[i + 1]
            values.append(value)

        received_crc = (data[12] << 8) + data[13]
        calculated_crc = zlib.crc32(bytes(data[:12])) & 0xFFFF

        if calculated_crc != received_crc:
            time.sleep(1)
            logging.info(f"CRC32 no coincide. Calculado: {calculated_crc}, Recibido: {received_crc}")
            return None

        logging.info(f"Data read successfully: {values}")
        return values
    except Exception as e:
        logging.error(f"Error reading data: {e}")
        return None

def send_data(alpha_list, beta_list):
    try:
        packed_alpha = b''.join(struct.pack('d', num) for num in alpha_list)
        packed_beta = b''.join(struct.pack('d', num) for num in beta_list)

        packed_data = packed_alpha + packed_beta
        crc_value = zlib.crc32(packed_data) & 0xFFFFFFFF
        packed_crc = struct.pack('I', crc_value)

        packed_data_with_crc = packed_data + packed_crc
        feedback = i2c_msg.write(DEVICE_ADDRESS, packed_data_with_crc)
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

alpha = [3.24892489, 4.324242, 5.432432]
beta = [-0.3427482, -0.5347832, -0.1123314]
while True:
    data = read_data()
    if data is not None:
        print("Data Recivied")
        save_to_csv(data,filename)
        send_data(alpha,beta)
    time.sleep(5)
