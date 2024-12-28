pellmonMQTT
===========

An MQTT client for *PellMon*.
This is an attempt to refactor/migrate from Python2.7 -> Python3.
Tested running python 3.12.7

**PellmonMQTT** connects to the PellMon DBUS interface and publishes all data at pellmon/_item_ and subscribes to all settings at pellmon/settings/_item_. Changed data items are republished and received data is written to the corresponding PellMon _item_. Events are published to pellmon/\_\_event\_\_.


#### Usage:
<pre>usage: pellmonMQTT [-h] -u user -p password [-H HOST] [-P PORT] [-d {SESSION,SYSTEM}]

options:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  mqtt host to connect to. Defaults to localhost
  -P PORT, --port PORT  network port to connect to. Defaults to 1883
  -t TOPIC, --topic TOPIC
                        Defines the topic to publish/listen to, default is pellmon
  -u USERNAME, --username USERNAME
                        Define a username which will be used to connect to the mqtt broker
  -p PASSWORD, --password PASSWORD
                        Define a password which will be used to connect to the mqtt broker
  -d {SESSION,SYSTEM}, --dbus {SESSION,SYSTEM}
                        which bus to use, SESSION is default</pre>

