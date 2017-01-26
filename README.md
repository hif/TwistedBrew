#TwistedBrew

Twisted Brew - Distributed brewing Software

This project is still in early design stages. 
More info will be added when it starts to take shape.

Design goals:

* Scalable brewing solution that can run on one or more devices
* The ability to read and use recipe info from [Beersmith](http://beersmith.com/)
* Server/Client design, one BrewMaster to rule them all (his workers) 

Master:

*   Parses recipe.bsmx from Beersmith and collects mash schedule, hop schedule and fermentation schedule
*   Can be monitored and controlled from a web GUI
*   Collects info from all BrewWorkers on the network for the user to control
*   Can assign brewing schedule(s) to available brewWorkers

Worker:

* Can manipulate various devices (Initially: SSR (Heating/Cooling element, pump), TempProb. Future: Electronic valve, FlowMeter, Servo)
* Can follow brewing schedule(s) which are assigned by a Master

The Twisted Pair (hif & hJod)  

---

##Install instructions

Install python development tools

    sudo -i
    apt-get -y install python-dev
    apt-get -y install python-pip

Install virtualenv, a virtual environment manager

    pip install virtualenv

Move to your preferred location and create your python 3 virtual environment

    virtualenv -p python3 twistedbrew

Activate your new environment (you can type in "deactivate" anywhere go back to your normal prompt)

    source twistedbrew/bin/activate

Get the latest version of TwistedBrew, unzip it, rename and clean up

    cd twistedbrew
    wget https://github.com/hif/TwistedBrew/archive/master.zip
    unzip master.zip
    mv TwistedBrew-master/ twistedbrew/
    rm master.zip

Install required packages

    sudo pip install -r twistedbrew/requirements.txt


##Usefull information

To start the Twisted Brew master and worker modules from config file (default is config/twisted_brew.yml), run:

    python manage.py twisted_brew

To use a specific config file add it's path as an optional parameter to the above command, example:

    python manage.py twisted_brew config/my_config_file.yml

###ZeroMQ requirements

Add **ipv6** in **/etc/modules** for ZeroMQ communication so that it survives reboot.

If you get a ZMQError when starting up, check the config file and make sure the IP address is correct.

###The DS18B20 temperature probe

To be able to use the probe you have to enabling the 1-wire communication device kernel modules in linux. Here is how it is done in Debian (also Rasbian).

Run these commands: `sudo modprobe w1-gpio && sudo modprobe w1_therm`

and then add **w1-gpio** and **w1_therm** in **/etc/modules** so that the mod survives reboot.

Excellent information on how to connect and work with the DS18B20 on Rasberry Pi can be found on this [website](http://www.reuk.co.uk/DS18B20-Temperature-Sensor-with-Raspberry-Pi.htm).

###Browser requirements

As our gui uses .bind() method in Javascript you have to use the following browsers:

*   Chrome 7 or higher
*   Firefox 4.0(2) or higher
*   IE 9 or higher
*   Opera 11.60 or higher
*   Safari 5.1.4 or higher

Required packages
* Django
* Django REST Framework
* pyYAML
* suit
* pytz
* pyzmq
