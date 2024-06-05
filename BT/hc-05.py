import serial
import time

# Configuración inicial del puerto serial
ser = serial.Serial(
    port='/dev/rfcomm0',  # Reemplaza con el puerto correcto en tu Raspberry Pi
    baudrate=9600,
    timeout=1
)

# Función para enviar datos al HC-05
def enviar_datos(data):
    ser.write(data.encode())

# Función para recibir datos del HC-05
def recibir_datos():
    while True:
        if ser.inWaiting() > 0:
            incoming_data = ser.readline().decode().strip()
            print("Datos recibidos:", incoming_data)
            break

# Ejemplo de uso
if __name__ == '__main__':
    try:
        while True:
            # Enviar un mensaje
            enviar_datos('Hola desde Raspberry Pi')
            time.sleep(1)

            # Recibir mensaje
                      recibir_datos()

    except KeyboardInterrupt:
        print("Programa terminado por el usuario")
        ser.close()
