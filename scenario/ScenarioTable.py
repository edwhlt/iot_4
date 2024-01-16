from PyQt5.QtWidgets import QTableWidget

from scenario.Row import Row


class ScenarioTable(QTableWidget):

    def __init__(self, scnRunner):
        super().__init__()
        self.scnRunner = scnRunner
        self.rows = []

    def addEmptyRow(self):
        self.addRow(index=self.rowCount(), name="", begin="0", end="24")

    def addRow(self, index, name, begin, end):
        row = Row(name, begin, end)
        print(row)
        self.rows.append(row)
        row.putOn(self, index=index)

    def removeScnRow(self):
        row = self.currentRow()
        if row >= 0:
            self.removeRow(row)
            self.rows.pop(row)
