import smbus
import time

bus = smbus.SMBus(1)
address = 0x42

def read_message():
    length = bus.read_byte(address)
    message = bus.read_i2c_block_data(address, 0, length)
    return ''.join(chr(i) for i in message)

while True:
    try:
        message = read_message()
        print("Message received:", message)
        time.sleep(1)
    except Exception as e:
        print("Error:", e)
        time.sleep(1)
