import sys

from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QPushButton, QMenu, QAction

from connection.MQTT import MqttClient
from connection.SQLFunctions import loadFromDB, createTableIfNotExists, saveToDB, saveValuesMQTT
from scenario.ScenarioTable import ScenarioTable
from scenario.ScenarionRunner import ScenarioRunner


class MyApp(QWidget):
    def __init__(self, client, scnRunner):
        super().__init__()
        self.mqtt_client = client
        self.scenarioRunner = scnRunner

        self.scenarioTable = ScenarioTable(self)
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
        loadFromDB(scenarioTable=self.scenarioTable)

    def initUI(self):
        self.relay_button.clicked.connect(self.toggle_relay)

        self.scenarioTable.setGeometry(50, 50, 400, 250)
        self.scenarioTable.setColumnCount(4)
        self.scenarioTable.setHorizontalHeaderLabels(['Name', 'Début', 'Fin', ''])
        self.scenarioTable.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scenarioTable.customContextMenuRequested.connect(self.showContextMenu)
        self.scenarioTable.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        # Create an Add Row button
        self.addRowButton.setGeometry(170, 320, 100, 30)
        self.addRowButton.clicked.connect(self.scenarioTable.addEmptyRow)

        # Create a Save button
        self.saveButton.setGeometry(50, 320, 100, 30)
        self.saveButton.clicked.connect(self.saveBtnAction)

        self.removeRowAction = QAction('Remove Row', self)
        self.removeRowAction.triggered.connect(self.scenarioTable.removeScnRow)
        self.contextMenu.addAction(self.removeRowAction)

        vbox = QVBoxLayout()
        vbox.addWidget(self.temperature_gauge)
        vbox.addWidget(self.humidity_bar)
        vbox.addWidget(self.motion_label)
        vbox.addWidget(self.relay_button)

        vbox.addWidget(self.scenarioTable)
        vbox.addWidget(self.addRowButton)
        vbox.addWidget(self.saveButton)

        self.setLayout(vbox)
        self.setWindowTitle('Mon application de gestion domotique')
        self.setGeometry(300, 300, 600, 800)
        icon = QIcon("assets/icon.png")  # Replace with the path to your icon file
        self.setWindowIcon(icon)
        self.show()

    def saveBtnAction(self):
        saveToDB(tableWidget=self.scenarioTable)

    def showContextMenu(self, pos):
        row = self.scenarioTable.indexAt(pos).row()
        if row >= 0:
            self.contextMenu.exec_(self.scenarioTable.mapToGlobal(pos))

    def update_temperature(self, temp):
        self.temperature_gauge.setText('Temperature: ' + temp)

    def update_humidity(self, humid):
        self.humidity_bar.setText('Humidity: ' + humid)

    def update_motion(self, motion):
        self.motion_label.setText('Motion: ' + motion)

    def toggle_relay(self):
        self.btnVal = not self.btnVal
        self.mqtt_client.publish("Room/rel", self.btnVal)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mqtt_client = MqttClient()
    scenarioRunner = ScenarioRunner()

    window = MyApp(mqtt_client, scenarioRunner)

    mqtt_client.setWindow(window)

    mqtt_client.connect("pi", 1883, 60)
    mqtt_client.loop_start()
    scenarioRunner.start()

    sys.exit(app.exec_())
