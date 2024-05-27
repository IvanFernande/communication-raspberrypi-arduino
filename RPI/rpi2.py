import smbus
import time
import sys

bus = smbus.SMBus(1)
address = 0x6b

def main():
    while True:
        # Enviar mensaje a Arduino
        message = "Yo bien, tu que tal?"
        bus.write_i2c_block_data(address, 0, [ord(c) for c in message])
        print("Raspberry Pi to Arduino: Yo bien, tu que tal?")
        
        # Esperar un poco antes de leer la respuesta
        time.sleep(1)
        
        # Leer la respuesta de Arduino
        response = bus.read_i2c_block_data(address, 0, 32)
        response_message = ''.join([chr(c) for c in response if c != 0])
        print("Arduino to Raspberry Pi:", response_message)
        
        # Esperar un poco antes de la siguiente iteración
        time.sleep(5)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        sys.exit(0)
