# I2C communication for a Raspberry Pi

## Introduction
This repository aims to collect different methods for communication between an Arduino MKR WAN 1310 and a Rapberrry Pi 3 model B+. The communication between these different devices is a key point in the IoT world as it allows devices at the edge to have a higher computational capacity without the need of an online server. 

During the development of these files, work was being done with a focus on agriculture, an area where the internet of things is crucial for monitoring soil moisture and irrigation data, as well as other necessary actions. 

In addition, by giving the spotlight to boards like the Rapberry Pi, the integration of AI into the internet of things, with applications such as complex data analysis, behavioural predictions and many more, is being driven!

Therefore, here are some example codes for use, to guide other users who are looking for such implementations.

### I2C (Inter-Integrated Circuit)
A physical connection protocol between two devices with the aim of making a larger IoT device can be a favourable option over others depending on the environment in which you want to work. Therefore, this type of communication was proposed and a series of tests were carried out to verify that this type of communication is viable. I2C is a serial communication port and protocol, which defines the data frame and physical connections to transfer data between 2 devices. The port includes two communication wires, SDA (data line) and SCL (data transfer synchronisation clock line). Both wires are connected to all devices that are connected to the bus. In addition, there is a third wire with ground (GND) common to all devices. This protocol allows up to 127 slave devices to be connected.

To connect the two devices, the pins shall be checked to locate the corresponding SCL and SDA pins on each board. This protocol is then configured on each board.
- In the case of **Arduino**, no configuration will be necessary.
- In the case of the **Raspberry Pi**, this had to be enabled.

The step for setting up the Raspberry Pi for the I2C are:
- A series of commands will be executed to update the system to ensure that we have the necessary tools that we have the necessary tools. These commands will be: 'sudo apt update', 'sudo apt upgrade' and lastly, with a focus on the I2C: 'sudo apt install i2c-tools'.
- Type 'sudo raspi-config' to enter a friendly computer configuration environment environment. Once we have confirmed that we want to enable this tool, it should indicate that it is now operational.
- Restart the system to apply the changes. In the case of using a desktop image desktop image, simply click on the logo button and select ‘Reboot’. In the case of using the Raspberry Pi via SSH, the command would be: 'sudo nano reboot -h now' to reboot it instantly.
- Once rebooted, run the command 'sudo i2cdetect -y 1' to search for connected devices on the I2C ports the devices connected to the I2C ports. If the devices are not found or any. If the devices are not found or an error occurs, access the 'config.txt' file of the Raspberry Pi. Once this is accessed, you should ensure that the following lines are uncommented, or at least the following lines are uncommented, or add them if they are not:
- 'dtparam=i2c arm=on'
- 'dtparam=i2c arm baudrate=100000'
- 'dtparam=i2c1=on'
We will then save the file and reboot to make sure that the changes are applied in the same way as in
changes are applied in the same way as in step 3.
- Finally, run the ‘sudo i2cdetect -y 1’ command again with the slave dispo-
Finally, run the command ‘sudo i2cdetect -y 1’ again with the slave device connected to the Raspberry Pi. It should then be found without any problem, as shown in the figure below.
problem, as shown in figure 81

On the other hand, this protocol I consists of a method to verify a successful sending of data from one point to another. Therefore, CRC32 was selected as the verification method. This is quite common within this domain thanks to the amount of documentation on this in the network. 

