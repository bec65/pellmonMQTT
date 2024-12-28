pellmonMQTT
===========

An MQTT client for *PellMon*.
This is an attempt to refactor/migrate from Python2.7 -> Python3.

**PellmonMQTT** connects to the PellMon DBUS interface and publishes all data at pellmon/_item_ and subscribes to all settings at pellmon/settings/_item_. Changed data items are republished and received data is written to the corresponding PellMon _item_. Events are published to pellmon/\_\_event\_\_.


#### Usage:
<pre>usage: pellmonMQTT [-h] -u user -p password [-H HOST] [-p PORT] [-d {SESSION,SYSTEM}]

optional arguments:
  -h, --help            show this help message and exit
  -H HOST, --host HOST  mqtt host to connect to. Defaults to localhost
  -u USER, --user USER  User id for connecting to MQTT server
  -p PASSWORD, --password PASSWORD  Password for connecting to MQTT server
  -P PORT, --port PORT  network port to connect to. Defaults to 1883
  -d {SESSION,SYSTEM}, --dbus {SESSION,SYSTEM}
                        which bus to use, SESSION is default</pre>

