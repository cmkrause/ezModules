from datetime import datetime
from ez.Table import *

class Timer:

    def __init__(self, title = "", realtimePrint = False, style = "AsciiTable", arcToolbox = False):
        self.reportData = []
        self.headers = ["Total Time", "Step Time", "Step Description"]
        self.title = title
        self.realtimePrint = realtimePrint
        self.printedHeader = False
        self.style = style

        ## https://stackoverflow.com/a/34179809
        self.arcToolbox = arcToolbox
        if self.arcToolbox == True:
            self.arcpy = __import__('arcpy')

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
            if self.arcToolbox == False:
                if self.printedHeader == False:
                    reportTable = ezTable(self.reportData, self.headers, title = self.title, display = False, style = self.style)
                    self.printedHeader = True
                else:
                    reportTable = ezTable([reportRow], display = False, style = self.style)
                print reportTable
            else:
                if self.printedHeader == False:
                    self.arcpy.AddMessage("\t\t".join([str(value) for value in self.headers]))
                    self.printedHeader = True
                self.arcpy.AddMessage("\t".join([str(value) for value in reportRow]))
            
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
