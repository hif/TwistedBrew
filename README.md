#TwistedBrew

Twisted Brew - Distributed brewing Software

This project is still in early design stages. 
More info will be added when it starts to take shape.

The Twisted Pair (hif & hJod)

#####The DS18B20 temperature probe

To be able to use the probe you have to enabling the 1-wire communication device kernel modules in linux. Here is how it is done in Debian (also Rasbian).

Run these commands: `sudo modprobe w1-gpio && sudo modprobe w1_therm`

and then add **w1-gpio** and **w1_therm** in **/etc/modules** so that the mod survives reboot.

Excellent information on how to connect and work with the DS18B20 on Rasberry Pi can be found on this [website](http://www.reuk.co.uk/DS18B20-Temperature-Sensor-with-Raspberry-Pi.htm).




