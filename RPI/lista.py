import csv
import logging
from smbus2 import SMBus, i2c_msg
import time
import pandas as pd
from datetime import datetime
from tensorflow import keras

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
        msg = i2c_msg.read(DEVICE_ADDRESS, 12)
        bus.i2c_rdwr(msg)

        data = list(msg)
        values = []
        for i in range(0, 12, 2):
            value = (data[i] << 8) + data[i + 1]
            values.append(value)
        
        logging.info(f"Data read successfully: {values}")
        return values
    except Exception as e:
        logging.error(f"Error reading data: {e}")
        return None

def save_to_csv(values, filename="data.csv"):
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

while True:
    data = read_data()
    if data is not None:
        save_to_csv(data)
    time.sleep(60)

