# HEPIA temperature monitoring

**Developed by:** Justin Foltz

**Date :** 01.2020

## The project

HEPIA temperature monitoring consists in setting up an infrastructure to monitor the evolution of the temperature of HEPIA's rooms. The data is collected from Raspberry installed in the different rooms and from the Bluetooth modules within range. The information is displayed in the form of graphs on a web interface. It is possible to monitor the evolution of the temperature from live data or to consult the history of the readings.

![](/home/justin/Documents/github/TemperatureMonitoring/img/desktop.jpg)

## Technologies

- Flask: API REST allowing to recover data from Raspberry and Bluetooth modules.

- Python : allows to send and retrieve data through an MQTT broker.

- MQTT : possibility to choose among the following brokers : broker.hivemq.com, mosquitto.org, test.mosquitto.org

- Javascript / HTML5 / CSS3 / Bootstrap : control web interface

- ChartJS: graphical representation of the evolution of data over time


## How to run the project

1. Clone the repository

2. Build and run the database from the `db` folder :

   ```bash
   cd db
   docker build . -t <name_container>:<version>
   docker run --rm -p27017:27017 <name_container>:<version>
   cd ..
   ```

3. Run the Rest server and the publisher/subscriber from the root folder :

   ```bash
   python3 restServer.py
   python3 mqtt_publisher.py
   python3 mqtt_subscriber.py
   ```

The web interface can be accessed at the following address: `localhost:5001`.

