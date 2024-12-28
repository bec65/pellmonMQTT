#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Copyright (C) 2013  Anders Nylund
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
#from builtins import object
from typing import Any
import sys
import argparse
from time import sleep
from gi.repository import Gio, GLib
import paho.mqtt.client as mqtt    # pylint: disable=E0401
import simplejson                  # pylint: disable=E0401

class DbusNotConnected(Exception):
    """Exception raised when there is an issue with the D-Bus connection.

    This exception is intended to be raised when a connection to the D-Bus
    is not established or is lost. It inherits from the built-in Exception
    class and allows for a custom error message to be provided.

    Attributes:
        message (str): A description of the error that occurred.
    """

    def __init__(self, message: str) -> None:
        """Initialize the DbusNotConnected exception with a message.

        Args:
            message (str): A message describing the reason for the exception.
        """
        super().__init__(message)
        print(f'DbusNotConnected: {message}')

#class Dbus_handler(object):
class DbusHandler:
    """Initialize the MyClass instance.

    Args:
        mq (str): The message queue identifier.
        bus (str): The bus type ('SYSTEM' or 'SESSION').
        mqtt_topic (str): The MQTT topic to subscribe to.
    """
    def __init__(self, mq, bus, mqtt_topic) -> None:
        if bus == 'SYSTEM':
            self.bustype = Gio.BusType.SYSTEM
        else:
            self.bustype = Gio.BusType.SESSION
        self.mq = mq
        self.mqtt_topic = mqtt_topic
        self.notify = None
        self.bus = None
        self.db = None
        self.settings = None

    def start(self) -> None:
        """ start """
        self.notify = None
        self.bus = Gio.bus_get_sync(self.bustype, None)
        Gio.bus_watch_name(
            self.bustype,
            'org.pellmon.int',
            Gio.DBusProxyFlags.NONE,
            self.dbus_connect,
            self.dbus_disconnect,
            )

    def dbus_connect(self, connection: Gio.DBusConnection, name: str, owner: str) -> None:
        """ dbus_connect """
        _ = connection    # Unused for now, but kept for future
        _ = name          # Unused for now, but kept for future
        _ = owner         # Unused for now, but kept for future

        self.notify = Gio.DBusProxy.new_sync(
            self.bus,
            Gio.DBusProxyFlags.NONE,
            None,
            'org.pellmon.int',
            '/org/pellmon/int',
            'org.pellmon.int',
            None)
        Status.dbus_connected = True
        #Publish all data items tagged with 'All' to pellmon/_item_
        self.db = self.notify.GetFullDB('(as)', ['All',])

        for item in self.db:
            try:
                value = self.get_item(item['name'])
                print(f"Publish {str(value)} to {self.mqtt_topic}/{item['name']}")
                self.mq.publish(f"{self.mqtt_topic}/{item['name']}", value, qos=2, retain=True)
            except RuntimeError as error:
                print(f'Exeption caught in Publish - dbus_connect: {error}')

    def subscribe(self) -> None:
        """Listen to the DBUS 'item changed' signal and publish changes at pellmon/_item_ """

        def on_signal(proxy, sender_name, signal_name, parameters):
            _ = proxy          # Unused for now, but kept for future
            _ = sender_name    # Unused for now, but kept for future
            _ = signal_name    # Unused for now, but kept for future

            parameter = parameters[0]
            msg = []
            msg = simplejson.loads(parameter)
            for dbusmsg in msg:
                self.mq.publish(f"{self.mqtt_topic}/{dbusmsg['name']}",
                                dbusmsg['value'],
                                qos=2,
                                retain=True)
                print(f"Publish {dbusmsg['value']} to {self.mqtt_topic}/{dbusmsg['name']}")
        #Subscribe to all data items tagged with 'Settings' at pellmon/settings/_item
        self.settings = self.notify.GetFullDB('(as)', ['All',])
        for item in self.settings:
            if item['type'] in ('W', 'R/W'):
                print(f"Subscribe to {self.mqtt_topic}/settings/{item['name']}")
                self.mq.subscribe(f"{self.mqtt_topic}/settings/{item['name']}")

        self.notify.connect("g-signal", on_signal)

    def dbus_disconnect(self, connection, name: str) -> None:
        """ dbus_disconnect """
        _ = connection         # Unused for now, but kept for future
        _ = name               # Unused for now, but kept for future

        Status.dbus_connected = False
        Status.subscribed = False
        if self.notify:
            self.notify = None

    def get_item(self, itm: str) -> Any:
        """ get_item """
        if self.notify:
            try:
                return self.notify.GetItem('(s)', str(itm))
            except RuntimeError:
                return 'error'
        else:
            raise DbusNotConnected("server not running")

    def set_item(self, item, value):
        """ set_item """
        if self.notify:
            return self.notify.SetItem('(ss)',item, str(value))
        raise DbusNotConnected("server not running")

    def getdb(self):
        """ getdb """
        if self.notify:
            return self.notify.GetDB()
        raise DbusNotConnected("server not running")

    def get_db_with_tags(self, tags):
        """ getDBwithTags """
        if self.notify:
            return self.notify.GetDBwithTags('(as)', tags)
        raise DbusNotConnected("server not running")

    def get_full_db(self, tags):
        """ getFullDB """
        if self.notify:
            db = self.notify.GetFullDB('(as)', str(tags))
            return db
        raise DbusNotConnected("server not running")

    def get_menutags(self):
        """ get_menutags """
        if self.notify:
            return self.notify.get_menutags()
        raise DbusNotConnected("server not running")

class Status:    # pylint: disable=R0903
    """ Class Status """
    mqtt_connected = False
    dbus_connected = False
    subscribed = False

if __name__ == '__main__':

    def on_connect(*args):
        """ on_connect """
        _ = args        # Unused for now, surpressing
        print("broker connected")
        Status.subscribed = False
        Status.mqtt_connected = True

    def on_publish(*args):
        """ What do when calling on_publish """
        _ = args        # Ignored, not used

    def on_subscribe(*args):
        """ on_subscribe """
        _ = args        # Ignored, not used

    def on_disconnect(*args):
        """ on_disconnect """
        _ = args        # Unused for now, surpressing
        print("Disconnecting from MQTT: ")
        #mqtt_connected = False
        Status.mqtt_connected = False

    def on_message(*args):
        """Call the DBUS set_item method with item name and payload
        from topic subscription at pellmon/settings/_item_"""
        print('subscribed item changed')
        msg = args[-1]
        item = msg.topic.split('/')[-1]
        try:
            dbus.set_item(item, msg.payload)
            print(f"Set {item}={msg.payload}, {dbus.set_item(item, msg.payload.decode('utf-8'))}" )
        except RuntimeError as error:
            print(f'Exception caught: {error}')

    def manager():
        """ Manager binding dbus and mqtt together """
        if not Status.subscribed:
            print('Manager: Not subscribed')
            if Status.dbus_connected and Status.mqtt_connected:
                print('Manager: subscribing...')
                dbus.subscribe()
                Status.subscribed = True
        return True

    parser = argparse.ArgumentParser(prog='pellmonMQTT')
    parser.add_argument('-H', '--host',
                        default='localhost',
                        help='mqtt host to connect to. Defaults to localhost')
    parser.add_argument('-P', '--port',
                        default='1883',
                        help='network port to connect to. Defaults to 1883')
    parser.add_argument('-d', '--dbus',
                        default='SESSION',
                        choices=['SESSION', 'SYSTEM'],
                        help='which bus to use, SESSION is default')
    parser.add_argument('-t', '--topic',
                        default='pellmon',
                        help='Defines the topic to publish/listen to, default is pellmon')
    parser.add_argument('-u', '--username',
                        default='',
                        help='Define a username which will be used to connect to the mqtt broker')
    parser.add_argument('-p', '--password',
                        default='',
                        help='Define a password which will be used to connect to the mqtt broker')
    arguments = parser.parse_args()

    #GObject.threads_init()

    # A main loop is needed for dbus "name watching" to work
    main_loop = GLib.MainLoop()

    GLib.timeout_add_seconds(1, manager)

    #create a broker
    mqttc = mqtt.Client(protocol=mqtt.MQTTv311)
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    mqttc.on_message = on_message

    print(f'topic: {arguments.topic} connecting on {arguments.dbus}')
    dbus = DbusHandler(mqttc, arguments.dbus, arguments.topic)
    dbus.start()

    CONNECT = False
    print("MQTT broker not connected yet..")
    while not CONNECT:
        try:
            mqttc.username_pw_set(username=arguments.username, password=arguments.password)
            mqttc.connect(arguments.host, int(arguments.port), 60)
            mqttc.reconnect_delay_set(min_delay=1, max_delay=120)
            CONNECT = True
        except KeyboardInterrupt:
            print("Error caught on connect")
            raise
        except mqtt.MQTTException as mqtt_error:
            print(f'MQTT error: {mqtt_error}')
            sleep(5)
        except OSError as os_error:
            print(f'OS error: {os_error}')
            sleep(5)
        # Catch-all for errors not handled previously.
        # Add pylint disable for Catching too general exception
        except Exception as error:               # pylint: disable=W0718
            print(f'An unspected error occured: {error}')
            sleep(5)

    print("MQTT broker Connected..")
    print(f'Python version: {str(sys.version)}')
    mqttc.loop_start()

    print(f'Connected to broker {arguments.host}')
    try:
        main_loop.run()
    except KeyboardInterrupt:
        print("Caught keyboard interrupt - MQTT broker leaving")
    finally:
        mqttc.loop_stop()
        mqttc.disconnect()
        if dbus.notify:
            dbus.dbus_disconnect(None, None)    # Call the disconnect method if needed
        print("End of Job")
