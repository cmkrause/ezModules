## Right now, this uses terminaltables
## https://github.com/Robpol86/terminaltables

## PTable is another good option, but it doesn't have the ability
## to distinguish a footer row
## https://github.com/kxxoling/PTable

## Arguably, tabulate is easier than both of the aforementioned
## https://pypi.python.org/pypi/tabulate

from terminaltables import *
import numpy
from copy import copy
import csv

def ezTable(data, columnHeaders = None, rowHeaders = None,
            summarizeColumns = None, summarizeRows = None,
            title = None, style = "SingleTable", display = True,
            returnFormat = "PRETTY"):

    # ------------------------------------------------------------
    # Make of a copy of the objects that will be modified so the
    # originals are not modified
    # http://docs.python-guide.org/en/latest/writing/gotchas/
    # http://stackoverflow.com/a/2612815
    # ------------------------------------------------------------
    data            = copy(data)
    columnHeaders   = copy(columnHeaders)
    rowHeaders      = copy(rowHeaders)
    # ------------------------------------------------------------
    
    # ------------------------------------------------------------
    # Determine if the data passed in is a numpy.ndarray
    # If so, make it a nested set of lists so every below works
    # http://docs.scipy.org/doc/numpy-1.10.0/reference/generated/numpy.ndarray.tolist.html
    # ------------------------------------------------------------
    if type(data) == type(numpy.ndarray([1])):
        data = data.tolist()
    # ------------------------------------------------------------

    # ------------------------------------------------------------
    # Define the summarizing functions
    # Summarize the columns and/or rows (if specified)
    # ------------------------------------------------------------
    def extractColumn(matrix, i):
        return [row[i] for row in matrix]

    def avg(l):
        ## http://stackoverflow.com/a/21600945
        return sum(l, 0.0) / len(l)

    if summarizeColumns <> None:
        footerRow = []
        if summarizeColumns == "SUM":
            for columnNumber in range(len(data[0])):
                footerRow.append(sum(extractColumn(data, columnNumber)))
        if summarizeColumns == "AVG":
            for columnNumber in range(len(data[0])):
                footerRow.append(avg(extractColumn(data, columnNumber)))
        data.append(footerRow)

    if summarizeRows <> None:
        for rowNumber in range(len(data)):
            if summarizeRows == "SUM":
                data[rowNumber].append(sum(data[rowNumber]))
            if summarizeRows == "AVG":
                data[rowNumber].append(avg(data[rowNumber]))
    # ------------------------------------------------------------

    # ------------------------------------------------------------
    # Update the columnHeaders or rowHeaders (if necessary)
    # ------------------------------------------------------------
    if summarizeColumns <> None and rowHeaders <> None:
        if summarizeColumns == "SUM":
            rowHeaders.append("Total")
        if summarizeColumns == "AVG":
            rowHeaders.append("Average")

    if summarizeRows <> None and columnHeaders <> None:
        if summarizeRows == "SUM":
            columnHeaders.append("Total")
        if summarizeRows == "AVG":
            columnHeaders.append("Average")
    # ------------------------------------------------------------
    
    # ------------------------------------------------------------
    # Add in the columnHeaders and/or rowHeaders (if specified)
    # ------------------------------------------------------------
    if rowHeaders == None and columnHeaders <> None:
        data.insert(0, columnHeaders)

    if rowHeaders <> None and columnHeaders <> None:
        data.insert(0, columnHeaders)
        rowHeaders.insert(0, "")
        for rowNumber in range(len(data)):
            data[rowNumber].insert(0, rowHeaders[rowNumber])

    if rowHeaders <> None and columnHeaders == None:
        for rowNumber in range(len(data)):
            data[rowNumber].insert(0, rowHeaders[rowNumber])
    # ------------------------------------------------------------
    
    # ------------------------------------------------------------
    # Convert everything to strings for display
    # ------------------------------------------------------------
    strData = []
    for row in data:
        strRow = []
        for value in row:
            strRow.append(str(value))
        strData.append(strRow)
    # ------------------------------------------------------------

    # ------------------------------------------------------------
    # Initalize the table and set the display parameters
    # ------------------------------------------------------------
    if style == "SingleTable":
        table = SingleTable(strData)
    elif style == "AsciiTable":
        table = AsciiTable(strData)
    elif style == "DoubleTable":
        table = DoubleTable(strData)
    elif style == "GithubFlavoredMarkdownTable":
        table = GithubFlavoredMarkdownTable(strData)
        
    if columnHeaders <> None:
        table.inner_heading_row_border = True
    else:
        table.inner_heading_row_border = False

    if summarizeColumns <> None:
        table.inner_footing_row_border = True

    if title <> None:
        table.title = title
    # ------------------------------------------------------------

    # ------------------------------------------------------------
    # Display the table (if requested) and then return it
    # ------------------------------------------------------------
    if display == True:
        print table.table

    if returnFormat == "PRETTY":
        return table.table
    elif returnFormat == "MATRIX":
        return data
    # ------------------------------------------------------------

def matrixToCSV(matrix, outputCSV):
    # Inspired from http://stackoverflow.com/a/14037564/6214388
    with open(outputCSV, "wb") as csvFile:
        writer = csv.writer(csvFile)
        writer.writerows(matrix)

if __name__ == "__main__":
    columnHeaders=["Col1", "Col2"]
    rowHeaders = ["Row1", "Row2"]
    ezTable(numpy.array([[1, 2], [3, 4]]), columnHeaders, rowHeaders, summarizeRows = "SUM", summarizeColumns = "SUM", title="Test")
    ezTable(numpy.array([[1, 2], [3, 4]]), columnHeaders, rowHeaders, title="Test")
