import threading
import time


class ScenarioRunner(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self, target=self.run)
        self.scenario = []

    def addScenario(self, scenario):
        self.scenario.append(scenario)

    def removeScenario(self, scenario):
        self.scenario.remove(scenario)

    def run(self):
        while True:
            for scn in self.scenario:
                print(scn.name)
            time.sleep(1)
