from machine import I2C, Pin
import time

# Configurar I2C
i2c = I2C(0, scl=Pin('P10'), sda=Pin('P9'))  # Ajusta los pines según tu conexión
i2c.init(I2C.MASTER, baudrate=100000)

address = 0x42  # Dirección I2C de la Raspberry Pi

def send_message(message):
    # Convertir el mensaje a bytes
    message_bytes = bytes(message, 'utf-8')
    # Enviar longitud del mensaje primero
    i2c.writeto(address, bytes([len(message_bytes)]))
    # Enviar el mensaje
    i2c.writeto(address, message_bytes)

while True:
    try:
        send_message("Hola Mundo")
        print("Mensaje enviado: Hola Mundo")
        time.sleep(5)
    except Exception as e:
        print("Error:", e)
        time.sleep(5)
