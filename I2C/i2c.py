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
        msg = i2c_msg.read(DEVICE_ADDRESS, 14)  # Read 14 bytes from the device
        bus.i2c_rdwr(msg)

        data = list(msg)  # Convert the message to a list of bytes
        values = []
        for i in range(0, 14, 2):
            value = (data[i] << 8) + data[i + 1]  # Combine bytes to get 16-bit values
            values.append(value)
        print(values)
        
        # Check if any value is 65535, indicating an error
        if 65535 in values:
            time.sleep(1)
            logging.info(f"Received values contain 65535")
            return None
        # Check if the last value is the expected quality value
        if values[-1] != 23456:
            time.sleep(1)
            logging.info(f"Quality value is incorrect")
            return None
        
        print("Data received ", values)
        logging.info(f"Data read successfully: {values}")
        
        values.pop(-1)  # Remove the quality value from the end
        return values
    except Exception as e:
        logging.error(f"Error reading data: {e}")
        return None

# Function to send data to the I2C device
def send_data(alpha_list, beta_list):
    try:
        packed_alpha = b''.join(struct.pack('d', num) for num in alpha_list)  # Pack the alpha list
        packed_beta = b''.join(struct.pack('d', num) for num in beta_list)    # Pack the beta list
        sleep_permission_ard = struct.pack('d', 0.2000)  # Pack the sleep permission time

        packed_data = packed_alpha + packed_beta + sleep_permission_ard  # Combine all packed data
        print(len(packed_data))

        feedback = i2c_msg.write(DEVICE_ADDRESS, packed_data)  # Create I2C message with packed data
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
