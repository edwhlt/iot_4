import sys
import time

import paho.mqtt.client as mqtt
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QTableWidget, QMenu, QAction

from SQLFunctions import loadFromPostgreSQL, createTableIfNotExists, saveValuesMQTT, saveToPostgreSQL


class MqttClient(mqtt.Client):
    last_save_times = {}  # Initialize a dictionary to store last save times for each topic

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
            window.update_temperature(str(msg.payload.decode()))
        elif msg.topic == "Room/hum":
            window.update_humidity(str(msg.payload.decode()))
        elif msg.topic == "Room/mouv":
            window.update_motion(str(msg.payload.decode()))

class MyApp(QWidget):
    def __init__(self, client):
        super().__init__()
        self.mqtt_client = client

        self.tableWidget = QTableWidget(self)
        self.contextMenu = QMenu(self)
        self.saveButton = QPushButton('Save', self)
        self.addRowButton = QPushButton('Add Row', self)

        self.temperature_gauge = QLabel('Temperature: --', self)
        self.humidity_bar = QLabel('Humidity: --', self)
        self.motion_label = QLabel('Motion: --', self)
        self.relay_button = QPushButton('Toggle Relay', self)

        self.btnVal = False

        self.initUI()
        createTableIfNotExists()
        loadFromPostgreSQL(tableWidget=self.tableWidget)

    def initUI(self):
        self.relay_button.clicked.connect(self.toggle_relay)

        self.tableWidget.setGeometry(50, 50, 400, 250)
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setHorizontalHeaderLabels(['Name', 'Début', 'Fin'])
        self.tableWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableWidget.customContextMenuRequested.connect(self.showContextMenu)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # Create an Add Row button
        self.addRowButton.setGeometry(170, 320, 100, 30)
        self.addRowButton.clicked.connect(self.addRow)

        # Create a Save button
        self.saveButton.setGeometry(50, 320, 100, 30)
        self.saveButton.clicked.connect(self.saveBtnAction)

        self.removeRowAction = QAction('Remove Row', self)
        self.removeRowAction.triggered.connect(self.removeRow)
        self.contextMenu.addAction(self.removeRowAction)

        vbox = QVBoxLayout()
        vbox.addWidget(self.temperature_gauge)
        vbox.addWidget(self.humidity_bar)
        vbox.addWidget(self.motion_label)
        vbox.addWidget(self.relay_button)

        vbox.addWidget(self.tableWidget)
        vbox.addWidget(self.addRowButton)
        vbox.addWidget(self.saveButton)

        self.setLayout(vbox)
        self.setWindowTitle('Mon application de gestion domotique')
        self.setGeometry(300, 300, 600, 800)
        icon = QIcon("icon.png")  # Replace with the path to your icon file
        self.setWindowIcon(icon)
        self.show()

    def addRow(self):
        rowPosition = self.tableWidget.rowCount()
        self.tableWidget.insertRow(rowPosition)

    def saveBtnAction(self):
        saveToPostgreSQL(tableWidget=self.tableWidget)

    def showContextMenu(self, pos):
        row = self.tableWidget.indexAt(pos).row()
        if row >= 0:
            self.contextMenu.exec_(self.tableWidget.mapToGlobal(pos))

    def removeRow(self):
        row = self.tableWidget.currentRow()
        if row >= 0:
            self.tableWidget.removeRow(row)

    def update_temperature(self, temp):
        self.temperature_gauge.setText('Temperature: ' + temp)

    def update_humidity(self, humid):
        self.humidity_bar.setText('Humidity: ' + humid)

    def update_motion(self, motion):
        # if bool(int(motion)):
        #     self.setStyleSheet("color: green;")
        # else:
        #     self.setStyleSheet("color: red;")

        self.motion_label.setText('Motion: ' + motion)

    def toggle_relay(self):
        self.btnVal = not self.btnVal
        self.mqtt_client.publish("Room/rel", self.btnVal)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mqtt_client = MqttClient()

    window = MyApp(mqtt_client)

    mqtt_client.connect("pi", 1883, 60)
    mqtt_client.loop_start()

    sys.exit(app.exec_())
