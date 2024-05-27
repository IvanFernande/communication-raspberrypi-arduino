import smbus2 as smbus
import time
import sys

bus = smbus.SMBus(1)
address = 0x6b

def write_number(value):
    bus.write_byte(address,value)
    time.sleep(0.1)

def read_number():
    number = bus.read_byte(address)
    return(number)

while True:
    number = int(input("Ingrese un numero:"))
    write_number = number
    print(f"RPI envió: {number}")

    reponse = read_number()
    print(f"RPI recibió: {reponse}")

time.sleep(1)
