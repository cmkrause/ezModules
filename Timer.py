from datetime import datetime
from ez.Table import *

class ezTimer:

    def __init__(self, title = "", realtimePrint = False, style = "AsciiTable"):
        self.reportData = []
        self.headers = ["Total Time", "Step Time", "Step Description"]
        self.title = title
        self.realtimePrint = realtimePrint
        self.printedHeader = False
        self.style = style

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
                reportTable = ezTable(self.reportData, self.headers, title = self.title, display = False, style = self.style)
                self.printedHeader = True
            else:
                reportTable = ezTable([reportRow], display = False, style = self.style)
            print reportTable
            return reportTable

    def report(self, display = True, outputFile = None):
        if len(self.reportData) > 0:
            reportTable = ezTable(self.reportData, self.headers, title = self.title, display = False, style = self.style)
        else:
            currentTime     = datetime.now()
            totalTimeDelta  = currentTime - self.timeZero
            reportTable = ezTable([[totalTimeDelta]], ["Total Time"], title = self.title, display = False, style = self.style)
        if display == True:
            print reportTable
        if outputFile <> None:
            f = open(outputFile, "w")
            f.write(reportTable)
            f.close()
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
