from __future__ import division
import arcpy
import os
from copy import copy
from ez.Misc import *
from ez.Describe import *
from ez.Table import *
from scipy.stats import chi2_contingency

def calcPercentageColumns(inputFC, columns):

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
    inputFC = "C:\\NHGIS\\NHGIS2010.gdb\\Blockgroups"

    ##print calcPercentageColumns(inputFC, ["CM1AA", "CM1AB", "CM1AC", "CM1AD", "CM1AE", "CM1AF", "CM1AG"])
    print "test"

    
