![alt_tag](https://github.com/joemcmanus/incidentMon/blob/main/images/redgreen.jpg)

# incidentMon
This collection of files allows you to monitor the Grafana IRM API https://grafana.com/products/cloud/irm/ and alert via MQTT. In this example it is monitored via an ESP32 that lights up. Video of it in use: https://youtu.be/H0PPRA18aig

# Software
The system is two parts, a python procuess that runs in a container or on a linux box running an MQTT broker plus a ESP32 for the vizualisation. 


On the linux box you will want to install mosquitto for the MQTT broker. The following works for ubuntu:

    sudo apt install mosquitto mosquitto-clients
   
# Parts used
![alt_tag](https://github.com/joemcmanus/incidentMon/blob/main/images/parts.jpg)

- https://www.sparkfun.com/sparkfun-pro-micro-esp32-c3.html
- https://www.sparkfun.com/sparkfun-qwiic-led-stick-apa102c.html
- Toy robot 

# Python Installation 

Copy the python file and .cfg into a folder, for this example I used `/home/joe/incidentMon`. Edit the .cfg to have your URL and your token. Leave the token blank and it will be accessed via environment variable `IRM_TOKEN`. 

To have it start on boot you will move the file `incidentMon.service` to /lib/systemd/system

    joe@jetson-3:~/incidentMon# sudo cp incidentMon.service /lib/systemd/system 
    joe@jetson-3:~/incidentMon# sudo systemctl enable incidentMon.service
    joe@jetson-3:~/incidentMon# sudo systemctl status incidentMon


# ESP32

I used a https://www.sparkfun.com/sparkfun-pro-micro-esp32-c3.html as the device, with a Sparkfun Qwiic LED. Load the .ino into the board and update the SSID, Wifi Password and MQTT Broker IP. 

ESP Troubleshooting
---
On power on it will blink blue 2x when the WiFi connection is successful. 

It will blink 5x white when the MQTT connection is established from the ESP32 to the Broker. 

You can send messages using mosquitto to test. 

    joe@jetson-3:~/incidentMon# mosquitto_pub -t ledOne -m "0" #Turns off all lights
    joe@jetson-3:~/incidentMon# mosquitto_pub -t ledOne -m "1" #Turns all lights blue
    joe@jetson-3:~/incidentMon# mosquitto_pub -t ledOne -m "2" #Turns all lights green
    joe@jetson-3:~/incidentMon# mosquitto_pub -t ledOne -m "3" #Turns all lights yellow
    joe@jetson-3:~/incidentMon# mosquitto_pub -t ledOne -m "4" #Turns all lights red
    joe@jetson-3:~/incidentMon# mosquitto_pub -t ledOne -m "5" #Turns all lights white

Python Troubleshooting
---
If you want verbose output you can pass `--debug(1|2)`.

 `--debug=1` will output config settings. 

 `--debug=2` will output config + dump json + print the token in use


# Python Options

    joe@jetson-3:~/incidentMon# ./incidentMon.py --help 
    usage: incidentMon.py [-h] [--debug DEBUG] [--pid] [--config CONFIG]
                          [--delay DELAY]
    
    Grafana IRM Monitor
    
    optional arguments:
      -h, --help       show this help message and exit
      --debug DEBUG    Turn on debug mode, levels 0-2,0=none, 1=info,2=dumps json
      --pid            Create a pid file in /var/run/incidentMon.pid
      --config CONFIG  Override config file location, default ./incidentMon.cfg
      --delay DELAY    Specify delay between checks, default 60s
      --mqtt MQTT      Enable MQTT, default true
      --security       Only act on Security incidents, ignore everything else


# Monitor security alerts only.
If you want to just monitor security alerts you can add `--security` .

# Skip MQTT
You may want to test your configuration or maybe have a terminal open just constantly watching the IRM api. To do that you can pass`--mqtt=false` to avoid sending data to your MQTT broker. 

# Token Handling
You probably don't want to store your API key(token) in plain text. You can use the environment variable `IRM_TOKEN` to store the API key. 
