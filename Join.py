import arcpy
from ez.Misc import *
from ez.Describe import *
from ez.FC import *

def joinTableToFC(inputTable, inputFC, joinField,
                  outputFC = None,
                  keepFieldsTable = "ALL", keepFieldsFC = "ALL"):

    inputTableView = randomString()
    arcpy.MakeTableView_management(inputTable, inputTableView)

    if type(joinField) is str:
        joinFieldTable  = joinField
        joinFieldFC     = joinField
    elif type(joinField) is list:
        joinFieldTable  = joinField[0]
        joinFieldFC     = joinField[1]

    if keepFieldsTable == "ALL":
        keepFieldsTable = listFieldNames(inputTableView)
    if type(keepFieldsTable) is str:
        keepFieldsTable = [keepFieldsTable] 

    if joinFieldTable not in keepFieldsTable:
        keepFieldsTable.insert(0, joinFieldTable)

    tableData = {}

    tableCursor = arcpy.da.SearchCursor(inputTableView, keepFieldsTable)
    for row in tableCursor:
        joinValue    = row[0]
        data         = row[1:]
        tableData[joinValue] = data
    del tableCursor

    ## In the case where no outputFC is specified, the data will be appended
    ## to the existing inputFC
    if outputFC == None:
        outputFC = inputFC
        ## Determine what (if any) fields do not currently exist
        ## and need to be created
        existingFields = listFieldNames(outputFC)
        fieldsToCopy = keepFieldsTable[1:]
        for existingField in existingFields:
            if existingField in fieldsToCopy:
                fieldsToCopy.remove(existingField)
        ## Create those fields using the fields in inputTable as a template
        copyFieldsToFC(inputTable, outputFC, fieldsToCopy)
    
    fcCursor = arcpy.da.UpdateCursor(outputFC, keepFieldsTable)
    for row in fcCursor:
        joinValue = row[0]
        if joinValue in tableData:
            data = tableData[joinValue]
            ## Concatenation of tuples explained:
            ## http://stackoverflow.com/a/8538676/6214388
            updatedRow = (joinValue, ) + data
            fcCursor.updateRow(updatedRow)
    del fcCursor
    
    return True

if __name__ == "__main__":

    inputTable = "C:\\NHGIS\\NHGIS_0008_2010.csv"
    inputFC = "C:\\NHGIS\\NHGIS2010.gdb\\Blockgroups"

    print joinTableToFC(inputTable, inputFC, "GISJOIN", keepFieldsTable=["CM1AA", "CM1AB", "CM1AC", "CM1AD", "CM1AE", "CM1AF", "CM1AG"])
