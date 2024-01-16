import time

import paho.mqtt.client as mqtt

from connection.SQLFunctions import saveValuesMQTT


class MqttClient(mqtt.Client):
    last_save_times = {}  # Initialize a dictionary to store last save times for each topic

    def __init__(self):
        super().__init__()
        self.window = None

    def setWindow(self, window):
        self.window = window

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        self.subscribe("Room/temp")
        self.subscribe("Room/hum")
        self.subscribe("Room/mouv")

    def on_message(self, client, userdata, msg):
        current_time = time.time()
        topic = msg.topic

        # Initialize the last_save_time for the topic if it doesn't exist
        if topic not in self.last_save_times: self.last_save_times[topic] = 0

        # Check if more than 1 minute has elapsed since the last save for this topic
        if current_time - self.last_save_times[topic] >= 60:
            saveValuesMQTT(msg)
            self.last_save_times[topic] = current_time  # Update the last save time for this topic

        if msg.topic == "Room/temp":
            self.window.update_temperature(str(msg.payload.decode()))
        elif msg.topic == "Room/hum":
            self.window.update_humidity(str(msg.payload.decode()))
        elif msg.topic == "Room/mouv":
            self.window.update_motion(str(msg.payload.decode()))