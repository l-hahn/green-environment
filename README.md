# green-environment

The indention of this project is to setup an application which can be used within greenhouses, that monitors environmental factors and partially is able to controle these.

The core of the project is to have a set of plants, where soil moisture sensors are integrated, next to sensors for air pressure, humidity, light intensity and temperature (gas meter are an interesseting aspect for the future aswell!).

With this application we then can for instance controll a pump to contril irrigation.

The first step is to implement a short commandline application in python, followed by a C++ application, which is/are then extended with a GUI and a live plotting of current values (temp etc.).


The hardware base will be a raspberry pi for sensor access.
The following sensors will be used:
- Gies-O-Mat soil moisture sensor from ramser-elektro.at is used
- TSL2591 Lux Sensor (or alternative) will be used for light parameter
- BME280 Pressure, Temperature, Humidity Sensor for air related parameters
- DS18B20 Waterproof temperature sensor for plant soil temperature

