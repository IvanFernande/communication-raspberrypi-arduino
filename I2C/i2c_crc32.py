import zlib
import csv
import logging
from smbus2 import SMBus, i2c_msg
import time
import pandas as pd
from datetime import datetime
import struct

# Set up logging
logging.basicConfig(filename='pruebai2c.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

# I2C device address
DEVICE_ADDRESS = 0x6b
# Initialize the I2C bus
bus = SMBus(1)

# CSV file name and column names
filename = "historial_datos.csv"
column_names = ["DateTime", "Sensor 0", "Sensor 1", "Sensor 2", "Sensor 3", "Sensor 4", "Sensor 5"]

# Create the CSV file if it doesn't exist
try:
    pd.read_csv(filename)
except FileNotFoundError:
    df = pd.DataFrame(columns=column_names)
    df.to_csv(filename, index=False)

# Function to read data from the I2C device
def read_data():
    try:
        msg = i2c_msg.read(DEVICE_ADDRESS, 16)  # Read 16 bytes instead of 14
        bus.i2c_rdwr(msg)

        data = list(msg)
        values = []
        for i in range(0, 12, 2):  # Read only the first 12 bytes as values
            value = (data[i] << 8) + data[i + 1]
            values.append(value)

        # Calculate and compare CRC32 checksums
        received_crc = (data[12] << 8) + data[13]
        calculated_crc = zlib.crc32(bytes(data[:12])) & 0xFFFF

        if calculated_crc != received_crc:
            time.sleep(1)
            logging.info(f"CRC32 mismatch. Calculated: {calculated_crc}, Received: {received_crc}")
            return None

        logging.info(f"Data read successfully: {values}")
        return values
    except Exception as e:
        logging.error(f"Error reading data: {e}")
        return None

# Function to send data to the I2C device
def send_data(alpha_list, beta_list):
    try:
        # Pack the alpha and beta lists as bytes
        packed_alpha = b''.join(struct.pack('d', num) for num in alpha_list)
        packed_beta = b''.join(struct.pack('d', num) for num in beta_list)

        packed_data = packed_alpha + packed_beta
        crc_value = zlib.crc32(packed_data) & 0xFFFFFFFF  # Calculate CRC32
        packed_crc = struct.pack('I', crc_value)  # Pack the CRC value

        packed_data_with_crc = packed_data + packed_crc  # Combine data and CRC
        feedback = i2c_msg.write(DEVICE_ADDRESS, packed_data_with_crc)  # Create I2C message
        bus.i2c_rdwr(feedback)  # Send I2C message

        logging.info(f'Data sent to Arduino: {alpha_list}, {beta_list}')
    except Exception as e:
        logging.error(f"Error sending data to Arduino: {e}")

# Function to save data to a CSV file
def save_to_csv(values, filename):
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Get current date and time

        # Create a dictionary with the data
        data = {
            "Timestamp": [timestamp],
            "Value1": [values[0]],
            "Value2": [values[1]],
            "Value3": [values[2]],
            "Value4": [values[3]],
            "Value5": [values[4]],
            "Value6": [values[5]],
        }

        df = pd.DataFrame(data)  # Create a DataFrame with the data

        df.to_csv(filename, mode='a', index=False, header=False)  # Save the DataFrame to the CSV file
        logging.info(f"Data saved to {filename}: {values}")
    except Exception as e:
        logging.error(f"Error saving data to {filename}: {e}")

# Example lists to send
alpha = [3.24892489, 4.324242, 5.432432]
beta = [-0.3427482, -0.5347832, -0.1123314]

# Main loop to read, save, and send data
while True:
    data = read_data()  # Read data from the device
    if data is not None:
        print("Data Received")
        save_to_csv(data, filename)  # Save the data to the CSV file
        send_data(alpha, beta)  # Send data to the device
    time.sleep(5)  # Wait 5 seconds before the next iteration
