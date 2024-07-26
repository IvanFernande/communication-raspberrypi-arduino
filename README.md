# I2C communication for a Raspberry Pi

## Introduction
This repository aims to collect different methods for communication between an Arduino MKR WAN 1310 and a Rapberrry Pi 3 model B+. The communication between these different devices is a key point in the IoT world as it allows devices at the edge to have a higher computational capacity without the need of an online server. 

During the development of these files, work was being done with a focus on agriculture, an area where the internet of things is crucial for monitoring soil moisture and irrigation data, as well as other necessary actions. 

In addition, by giving the spotlight to boards like the Rapberry Pi, the integration of AI into the internet of things, with applications such as complex data analysis, behavioural predictions and many more, is being driven!

Therefore, here are some example codes for use, to guide other users who are looking for such implementations.

![image](https://github.com/IvanFernande/i2c-communication-raspberrypi/assets/149154386/4a0fb3e4-0a36-4861-8dbf-a7145b964aac)

### I2C (Inter-Integrated Circuit)
A physical connection protocol between two devices with the aim of making a larger IoT device can be a favourable option over others depending on the environment in which you want to work. Therefore, this type of communication was proposed and a series of tests were carried out to verify that this type of communication is viable. I2C is a serial communication port and protocol, which defines the data frame and physical connections to transfer data between 2 devices. The port includes two communication wires, SDA (data line) and SCL (data transfer synchronisation clock line). Both wires are connected to all devices that are connected to the bus. In addition, there is a third wire with ground (GND) common to all devices. This protocol allows up to 127 slave devices to be connected.

To connect the two devices, the pins shall be checked to locate the corresponding SCL and SDA pins on each board. This protocol is then configured on each board.
- In the case of **Arduino**, no configuration will be necessary.
- In the case of the **Raspberry Pi**, this had to be enabled. 

On the other hand, this protocol I consists of a method to verify a successful sending of data from one point to another. Therefore, CRC32 was selected as the verification method. This is quite common within this domain thanks to the amount of documentation on this in the network. 

