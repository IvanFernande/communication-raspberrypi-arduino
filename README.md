# I2C and Bluetooth communication between Arduino and Raspberry Pi

This repository aims to collect different methods for communication between an Arduino MKR WAN 1310 and a Rapberrry Pi 3 model B+. The communication between these different devices is a key point in the IoT world as it allows devices at the edge to have a higher computational capacity without the need of an online server. 

During the development of these files, work was being done with a focus on agriculture, an area where the internet of things is crucial for monitoring soil moisture and irrigation data, as well as other necessary actions. 

In addition, by giving the spotlight to boards like the Rapberry Pi, the integration of AI into the internet of things, with applications such as complex data analysis, behavioural predictions and many more, is being driven!

Therefore, here are some example codes for use, to guide other users who are looking for such implementations.

## I2C (Inter-Integrated Circuit)
A physical connection protocol between two devices with the aim of making a larger IoT device can be a favourable option over others depending on the environment in which you want to work. Therefore, this type of communication was proposed and a series of tests were carried out to verify that this type of communication is viable. I2C is a serial communication port and protocol, which defines the data frame and physical connections to transfer data between 2 devices. The port includes two communication wires, SDA (data line) and SCL (data transfer synchronisation clock line). Both wires are connected to all devices that are connected to the bus. In addition, there is a third wire with ground (GND) common to all devices. This protocol allows up to 127 slave devices to be connected.

To connect the two devices, the pins shall be checked to locate the corresponding SCL and SDA pins on each board. This protocol is then configured on each board.
- In the case of **Arduino**, no configuration will be necessary.
- In the case of the **Raspberry Pi**, this had to be enabled.

The step for setting up the Raspberry Pi for the I2C are:
1. A series of commands will be executed to update the system to ensure that we have the necessary tools that we have the necessary tools. These commands will be: ```sudo apt update```, ```sudo apt upgrade``` and lastly, with a focus on the I2C: ```sudo apt install i2c-tools```.
2. Type ```sudo raspi-config``` to enter a friendly computer configuration environment environment. Once we have confirmed that we want to enable this tool, it should indicate that it is now operational.
3. Restart the system to apply the changes. In the case of using a desktop image desktop image, simply click on the logo button and select ‘Reboot’. In the case of using the Raspberry Pi via SSH, the command would be: ```sudo nano reboot -h now``` to reboot it instantly.
4. Once rebooted, run the command ```sudo i2cdetect -y 1``` to search for connected devices on the I2C ports the devices connected to the I2C ports. If the devices are not found or any. If the devices are not found or an error occurs, access the 'config.txt' file of the Raspberry Pi. Once this is accessed, you should ensure that the following lines are uncommented, or at least the following lines are uncommented, or add them if they are not:
  - ```dtparam=i2c arm=on```
  - ```dtparam=i2c arm baudrate=100000```
  - ```dtparam=i2c1=on```
We will then save the file and reboot to make sure that the changes are applied in the same way as in
changes are applied in the same way as in step 3.
5. Finally, run the command ```sudo i2cdetect -y 1``` again with the slave device connected to the Raspberry Pi. It should then be found without any problem, as shown in the figure below.
problem, as shown in the next figure.

![image](https://github.com/user-attachments/assets/b5ab9874-c346-485e-bd1c-104fdb2218de)

Once the devices have been configured, the necessary libraries will be installed to establish the communication, as well as the transformation of the data into bytes so that they can be transmitted by this protocol.

Subsequently, a recapitulation of the new Python and C++ libraries will be made in order to make this possible in the most orderly way possible.

- struct (Python): Used to convert between byte strings and Python value representations (e.g. integers and decimals).

- smbus2 (Python): Provides functions for communicating with I2C devices via the SMBus (System Management Bus).

- Wire (C++): Allows the Arduino board to act as a master or slave to send and receive data with other devices connected via I2C.

So far, these are the steps for configuring and sending data via I2C communication. However, it lacks a method to verify that the data has been sent correctly. For this, we have used the CRC32 method, which can be used in Arduino thanks to the CRC32 library and in Python thanks to the zlib library.

Once the configuration steps have been followed, the codes in the I2C folder can be executed.

## Bluetooth
Wireless connection between two devices for the purpose of creating an IoT tool is a favourite option because it does not rely on any wiring to transmit information from the sensors to the more computationally capable device and vice versa.

The Raspberry Pi used in this repository has the possibility of bluetooth connection, but the Arduino board, on the other hand, does not.  That is why, in order to provide the Arduino board with this type of connection, an HC-05 was used, which consists of a device connected to the TX and RX pins that allows receiving and sending data through this protocol (when connected to the TX and RX pins, it is known that this communication will be serial).

To configure this device, the AT commands shall be used. These are used to find out the visible device name, baud rate, whether it is in slave mode, and more information.
Once the module has been configured, the Raspberry Pi will be connected to the module, and a test will be made to ensure that the connection has been made correctly.

To do this, tools must be installed and a series of steps must be followed to obtain the address of this device for a future connection.
- ```sudo apt-get update```
- ```sudo apt-get install bluetooth ```

After this installation, we need to activate the Bluetooth service. This is done by executing the following commands:

- ```sudo systemctl enable bluetooth```
- ```sudo systemctl start bluetooth```

Next, the status of the Bluetooth adapter must be checked; this is done by running the command ```sudo hciconfig hci0 up```. Once these lines do not fail, you can use the ```hciconfig``` command. If this returns data such as the address of the Raspberry Pi, as well as the number of bits it can send via TX and receive via RX, then our computer is ready to search for our Bluetooth module in user mode. 

To find out the address of the module in our Raspberry Pi, we run ```hcitool scan```. You should then see a message saying ''Scanning...'' to let you know that it will be searching for nearby bluetooth devices. Finally, it will find our HC-05 module with its address. 

But if this is not enough, there are other methods for scanning for devices to find their addresses. In this case, the command ```bluetoothctl``` must be executed to interact with the Bluetooth devices. This command will open a console, where the following commands will be executed:

- ```power on``` to turn on the bluetooth controller.
- ```agent on``` to enable discovery mode.
- ```scan on``` and ```scan off``` to start and stop scanning for devices. Once it finds them, their MAC addresses and names will be displayed. 

![image](https://github.com/user-attachments/assets/7da6a3b7-7b03-4652-969a-c5e2d86709d7)


