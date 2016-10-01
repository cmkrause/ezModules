from datetime import datetime
from ez.Table import *

class ezTimer:

    def __init__(self, title = "", realtimePrint = False):
        self.reportData = []
        self.headers = ["Total Time", "Step Time", "Step Description"]
        self.title = title
        self.realtimePrint = realtimePrint
        self.printedHeader = False

        self.timeZero = datetime.now()
        self.lastTime = self.timeZero
        

    def update(self, description=""):
        currentTime     = datetime.now()
        totalTimeDelta  = currentTime - self.timeZero
        actionTimeDelta = currentTime - self.lastTime

        reportRow       = [totalTimeDelta, actionTimeDelta, description]
        self.reportData.append(reportRow)

        self.lastTime = currentTime

        if self.realtimePrint == True:
            if self.printedHeader == False:
                reportTable = ezTable(self.reportData, self.headers, title = self.title, display = False)
                self.printedHeader = True
            else:
                reportTable = ezTable([reportRow], display = False)
            print reportTable
            return reportTable

    def report(self, displayReport = True, reportToFile = None):
        if len(self.reportData) > 0:
            reportTable = ezTable(self.reportData, self.headers, title = self.title, display = False)
        else:
            currentTime     = datetime.now()
            totalTimeDelta  = currentTime - self.timeZero
            reportTable = ezTable([[totalTimeDelta]], ["Total Time"], title = self.title, display = False)
        if displayReport == True:
            print reportTable
        return reportTable

if __name__ == "__main__":
    from random import randint
    from time import sleep
    timer = ezTimer("Timer Test")
    for i in range(3):
        sleepTime = randint(3, 5)
        sleep(sleepTime)
        timer.update("Slept for %s second" % sleepTime)
    timer.report()
