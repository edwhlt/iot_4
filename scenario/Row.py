from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton, QTableWidgetItem

from scenario.Scenario import Scenario


class Row():
    def __init__(self, name, debut, fin):
        self.scnTable = None
        self.index = None
        self.scenario = Scenario(str(name), str(debut), str(fin))

        self.button = QPushButton()
        self.button.setIcon(QIcon("../assets/start.svg"))
        self.button.clicked.connect(self.toggleScn)
        self.scn_running = False

    def toggleScn(self):
        print("test")
        if self.scnTable is None: raise Exception("ScenarioTable is None")
        if self.scn_running:
            print("stop")
            self.button.setIcon(QIcon("../assets/start.svg"))
            self.scnTable.scnRunner.addScenario(scenario=self.scenario)
        else:
            print("start")
            self.button.setIcon(QIcon("../assets/stop.svg"))
            self.scnTable.scnRunner.removeScenario(scenario=self.scenario)

        self.scn_running = not self.scn_running
        self.scnTable.setCellWidget(self.index, 3, self.button)

    def putOn(self, scnTable, index):
        self.scnTable = scnTable
        self.index = index
        self.scnTable.setItem(index, 0, QTableWidgetItem(self.scenario.name))
        self.scnTable.setItem(index, 1, QTableWidgetItem(self.scenario.begin))
        self.scnTable.setItem(index, 2, QTableWidgetItem(self.scenario.end))
        self.scnTable.setCellWidget(index, 3, self.button)
        print(index)
