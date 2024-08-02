import serial
import time

# Initial configuration of the serial port
ser = serial.Serial(
    port='/dev/rfcomm0',  # Replace with the correct port on your Raspberry Pi
    baudrate=9600,
    timeout=1
)

# Function to send data to the HC-05
def enviar_datos(data):
    ser.write(data.encode())  # Encode and write the data to the serial port

# Function to receive data from the HC-05
def recibir_datos():
    while True:
        if ser.inWaiting() > 0:  # Check if there is data waiting to be read
            incoming_data = ser.readline().decode().strip()  # Read, decode, and strip the incoming data
            print("Data received:", incoming_data)  # Print the received data
            break  # Exit the loop after receiving data

# Example usage
if __name__ == '__main__':
    try:
        while True:
            # Send a message
            enviar_datos('Hello from Raspberry Pi')
            time.sleep(1)  # Wait for 1 second

            # Receive message
            recibir_datos()

    except KeyboardInterrupt:
        print("User terminated programme")  # Print a message when the program is terminated by the user
        ser.close()  # Close the serial port
