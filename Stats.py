from __future__ import division
import arcpy
import os
from copy import copy
from ez.Misc import *
##from ez.Describe import *
from ez.Table import *
from scipy.stats import chi2_contingency
from numpy import percentile

## This class is from https://github.com/liyanage/python-modules/blob/master/running_stats.py
## It was originally based on http://www.johndcook.com/standard_deviation.html
class runningStats:

    def __init__(self):
        self.n = 0
        self.old_m = 0
        self.new_m = 0
        self.old_s = 0
        self.new_s = 0
    
    def clear(self):
        self.n = 0
        
    def push(self, x):
        self.n += 1
        
        if self.n == 1:
            self.old_m = self.new_m = x
            self.old_s = 0
        else:
            self.new_m = self.old_m + (x - self.old_m) / self.n
            self.new_s = self.old_s + (x - self.old_m) * (x - self.new_m)
            
            self.old_m = self.new_m
            self.old_s = self.new_s

    def mean(self):
        return self.new_m if self.n else 0.0
    
    def variance(self):
        return self.new_s / (self.n - 1) if self.n > 1 else 0.0
        
    def stdDev(self):
        return math.sqrt(self.variance())


## This function creates percentage columns
## The total parameter controls how the percentages are calculated
## When total = "COLUMN"
##      This function takes a column and calculates a new column
##      with the percentage of that column total
##      For example, if you had a data table like
##      GEOID | Pop2010
##      ---------------
##      27    | 100
##      28    | 200
##      29    | 200
##      This function would update the table to
##      GEOID | Pop2010 | PCT_Pop2010
##      -----------------------------
##      27    | 100     | 0.2
##      28    | 200     | 0.4
##      29    | 200     | 0.4
##
##      columns may be a string instead of a list if calculating a single
##      column is desired
## When total = "ROW"
##      This function takes a list of columns and calculates new columns
##      each with the percentage of that row total
##      For example, if you had a data table like
##      White | Black | Other
##      ---------------------
##      100   | 50    | 50
##      This function would update the table to
##      White | Black | Other | PCT_White | PCT_Black | PCT_Other
##      ---------------------------------------------------------
##      100   | 50    | 50    | 0.5       | 0.25      | 0.25
def calcPercentageColumns(inputFC, columns, total = "COLUMN"):
    if total == "COLUMN":
        if type(columns) == str:
            columns = [columns]

        columnSums = []

        for column in columns:
            percentColumn = "PCT_%s" % column
            arcpy.AddField_management(inputFC, percentColumn, "DOUBLE")
            columnSums.append(fieldSum(inputFC, column)) 

        cursorColumns = copy(columns)
        for column in columns:
            cursorColumns.append("PCT_%s" % column)

        cursor = arcpy.da.UpdateCursor(inputFC, cursorColumns)
        for row in cursor:
            dataValues  = copy(row[:len(columns)])
            for columnNumber in range(len(columns)):
                percentage = dataValues[columnNumber] / columnSums[columnNumber]
                dataValues.append(percentage)
            cursor.updateRow(dataValues)
        del cursor


    if total == "ROW":
        for column in columns:
            arcpy.AddField_management(inputFC, "PCT_%s" % column, "DOUBLE")

        cursorColumns = copy(columns)
        for column in columns:
            cursorColumns.append("PCT_%s" % column)

        cursor = arcpy.da.UpdateCursor(inputFC, cursorColumns)
        for row in cursor:
            dataValues  = copy(row[:len(columns)])
            dataSum     = sum(dataValues)
            if dataSum > 0:
                for columnNumber in range(len(columns)):
                    percentage = dataValues[columnNumber] / dataSum
                    dataValues.append(percentage)
                cursor.updateRow(dataValues)
        del cursor

    return True

class quantileCalculator:
    def __init__(self, data, n = 4, interpolationMethod = "linear"):
        self.valueRanges = []
        for i in range(1, n + 1):
            lowerPercentile = (100 / n) * (i - 1)
            upperPercentile = (100 / n) * i

            lowerPercentileValue = percentile(data, lowerPercentile, interpolation = interpolationMethod)
            upperPercentileValue = percentile(data, upperPercentile, interpolation = interpolationMethod)

            self.valueRanges.append([lowerPercentileValue, upperPercentileValue])

    def __call__(self, x):
        for i in  xrange(len(self.valueRanges)):
            lowerLimit, upperLimit  = self.valueRanges[i]
            if x >= lowerLimit and x < upperLimit:
                return i + 1
            ## Special case for the top value
            if i + 1 == len(self.valueRanges) and x == upperLimit:
                return i + 1

def calcQuantileColumns(inputFC, columns, n):
    if type(columns) == str:
        columns = [columns]

    for column in columns:
        newColumn = "QNT_%s" % column
        arcpy.AddField_management(inputFC, newColumn, "SHORT")
        quantiles = quantileCalculator(fieldValues(inputFC, column), n)

        cursor = arcpy.da.UpdateCursor(inputFC, [column, newColumn])
        for row in cursor:
            if row[0] <> None:
                cursor.updateRow([row[0], quantiles(row[0])])
            else:
                cursor.updateRow([None, None])
        del cursor

    return True

def contigencyAnalysis(dataTable,
                       rowNames = None, columnNames = None,
                       display = True, outputFile = None):
    
    testStatistic, pValue, degreesOfFreedom, expectedTable = chi2_contingency(dataTable)

    
    outputDataTable = ezTable(dataTable, columnNames, rowNames, summarizeColumns ="SUM", summarizeRows = "SUM", title = "Observed Counts", display = display, returnFormat = "MATRIX")

    outputExpectedTable = ezTable(expectedTable, columnNames, rowNames, summarizeColumns ="SUM", summarizeRows = "SUM", title = "Expected Counts", display = display, returnFormat = "MATRIX")

    if 0.0001 > pValue:
        pValueString = "< 0.0001"
    else:
        pValueString = str(round(pValue, 4))
    
    resultsTable = [["Test Statistic", testStatistic],
                    ["Degrees of Freedom", degreesOfFreedom],
                    ["p-value", pValueString]]

    outputResultsTable = ezTable(resultsTable, title="Results", display = display, returnFormat = "MATRIX")

    if outputFile <> None:
        outputMatrix = outputDataTable + [['']] + outputExpectedTable + [['']] + outputResultsTable
        matrixToCSV(outputMatrix, outputFile)

    return testStatistic, pValue, degreesOfFreedom, expectedTable

def contigencyTable1FC(inputFC, rowQueries, columnQueries,
                       columnNames = None, rowNames = None,
                       display = True, outputFile = None):
    dataTable = []

    inputLYR = randomString()
    arcpy.MakeFeatureLayer_management(inputFC, inputLYR)

    for rowQuery in rowQueries:
        newRow = []
        for columnQuery in columnQueries:
            query = "(%s) AND (%s)" % (rowQuery, columnQuery)
            newRow.append(countFeatures(inputLYR, query))
        dataTable.append(newRow)

    return contigencyAnalysis(dataTable, rowNames, columnNames, display, outputFile)

def contigencyTable2FC(pointFC, polygonFC, pointQueries, polygonQueries,
                       pointNames = None, polygonNames = None,
                       display = True, outputFile = None):

    pointLYR = randomString()
    polygonLYR = randomString()

    arcpy.MakeFeatureLayer_management(polygonFC, polygonLYR)
    arcpy.MakeFeatureLayer_management(pointFC, pointLYR)

    dataTable = []

    for polygonQuery in polygonQueries:
        newRow = []
        arcpy.SelectLayerByAttribute_management(polygonLYR,where_clause = polygonQuery)
        for pointQuery in pointQueries:
            arcpy.SelectLayerByAttribute_management(pointLYR, where_clause = pointQuery)
            arcpy.SelectLayerByLocation_management(pointLYR, select_features = polygonLYR, selection_type = "SUBSET_SELECTION")
            newRow.append(countFeatures(pointLYR))
        dataTable.append(newRow)

    return contigencyAnalysis(dataTable, polygonNames, pointNames, display, outputFile)
    

if __name__ == "__main__":
    ##inputFC = "C:\\NHGIS\\NHGIS2010.gdb\\Blockgroups"

    ##print calcPercentageColumns(inputFC, ["CM1AA", "CM1AB", "CM1AC", "CM1AD", "CM1AE", "CM1AF", "CM1AG"])
    ##print "test"

    #inputTBL = "C:\\MasterThesis\\Spring2017\\Metros_Analysis\\Extra.gdb\\OD_BG_G19140_Statistics"    

    #calcPercentageColumns(inputTBL, "SUM_ADKXE001")

    inputTBL = "C:\\MasterThesis\\Spring2017\\Metros_Analysis\\Extra.gdb\\OD_BG_G19140"

    calcQuantileColumns(inputTBL, ["ADNKE001", "ADRWE001"], 4)
