import arcpy
from ez.Misc import *
from ez.Describe import *
from ez.FC import *
from ez.Timer import *
import os

def joinTables(inputTables, joinField, outputTable, scratchWorkspace = "in_memory"):

    largestTable    = ""
    largestN        = 0

    for table in inputTables:
        rowCount = countFeatures(table)
        if rowCount > largestN:
            largestTable = table
            largestN = rowCount

    intermediateCount = 0
    for table in inputTables:
        if intermediateCount == 0:
            inputTable = largestTable
        else:
            inputTable = os.path.join(scratchWorkspace, "Output_%s" % (intermediateCount - 1))

        if table <> largestTable:
            intermediateTable = os.path.join(scratchWorkspace, "Output_%s" % intermediateCount)
            joinTableToFC(inputTable, table, joinField, intermediateTable)
            intermediateCount += 1

    finalIntermediate = os.path.join(scratchWorkspace, "Output_%s" % (intermediateCount - 1))
    TableToTable(finalIntermediate, outputTable)

    return True
    

def joinTableToFC(inputTable, inputFC, joinField,
                  outputFC = None, fieldMappings = "ALL",
                  chunkSize = None):

    #timer = ezTimer()

    inputTableView = randomString()
    arcpy.MakeTableView_management(inputTable, inputTableView)

    ## joinField can either be a string or a list.
    ## Specifying a string means that a field with that name
    ## is common to both the inputTable and the inputFC.
    ## If there is not a common name, provide a list where
    ## the first element is the name of the field in the inputTable
    ## and the second element is the name of the field in the inputFC
    if type(joinField) is str:
        joinFieldTable  = joinField
        joinFieldFC     = joinField
    elif type(joinField) is list:
        joinFieldTable  = joinField[0]
        joinFieldFC     = joinField[1]

##    if keepFieldsTable == "ALL":
##        keepFieldsTable = listFieldNames(inputTableView)
##    if type(keepFieldsTable) is str:
##        keepFieldsTable = [keepFieldsTable] 
##
##    if joinFieldTable not in keepFieldsTable:
##        keepFieldsTable.insert(0, joinFieldTable)
##
##    ## In the case where no outputFC is specified, the data will be appended
##    ## to the existing inputFC
##    if outputFC == None:
##        outputFC = inputFC
##        ## Determine what (if any) fields do not currently exist
##        ## and need to be created
##        existingFields = listFieldNames(outputFC)
##        fieldsToCopy = keepFieldsTable[1:]
##        for existingField in existingFields:
##            if existingField in fieldsToCopy:
##                fieldsToCopy.remove(existingField)
##        ## Create those fields using the fields in inputTable as a template
##        copyFieldsToFC(inputTable, outputFC, fieldsToCopy)
##
##    timer.update("Creating fields for join data")

    if outputFC == None:
        outputFC = inputFC
    ## This else might not actually work
    else:
        if arcpy.Describe(inputFC).dataType == "Table":
            TableToTable(inputFC, outputFC)
        else:
            FCToFC(inputFC, outputFC)

    if fieldMappings <> "ALL":
        scFields = [joinFieldTable]
        ucFields = [joinFieldFC]
        for fieldMap in fieldMappings:
            if type(fieldMap) is list:
                scFields.append(fieldMap[0])
                ucFields.append(fieldMap[1])
            elif type(fieldMap) is str:
                scFields.append(fieldMap)
                ucFields.append(fieldMap)
    else:
        scFields = [joinFieldTable]
        ucFields = [joinFieldFC]
##        ucExistingFields = listFieldNames(outputFC)
##        for ucExistingField in ucExistingFields:
##            if ucExistingField not in ucFields:
##                ucFields.append(ucExistingField)
        scExistingFields = listFieldNames(inputTableView)
        for scExistingField in scExistingFields:
            if scExistingField not in scFields:
                scFields.append(scExistingField)
            if scExistingField not in ucFields:
                ucFields.append(scExistingField)
##    print scFields
##    print ucFields
                
    ## Determine if the fields that are to be joined exist in the outputFC
    ## If they do not exist, create them
    ucExistingFields = listFieldNames(outputFC)
    ucFieldsToCopy = []
    for ucField in ucFields:
        if ucField not in ucExistingFields:
            ucFieldsToCopy.append(ucField)
##    print ucFieldsToCopy
    copyFieldsToFC(inputTableView, outputFC, ucFieldsToCopy)
    

    

    with arcpy.da.SearchCursor(inputTableView, scFields) as tableCursor:
        
        if chunkSize == None:
            chunkSize = 10**9
            
        chunks = chunkIterable(tableCursor, chunkSize)
        
        for tableCursorChunk in chunks:
            tableData = {}
            
            for row in tableCursorChunk:
                joinValue    = row[0]
                data         = row[1:]
                tableData[joinValue] = data

            #timer.update("Creating in-memory dictionary")

            
            
            fcCursor = arcpy.da.UpdateCursor(outputFC, ucFields)
            for row in fcCursor:
                joinValue = row[0]
                if joinValue in tableData:
                    data = tableData[joinValue]
                    ## Concatenation of tuples explained:
                    ## http://stackoverflow.com/a/8538676/6214388
                    updatedRow = (joinValue, ) + data
##                    print ucFields
##                    print updatedRow
                    fcCursor.updateRow(updatedRow)
            del fcCursor

            #timer.update("Joining with update cursor")

            #timer.report()
    
    return True

if __name__ == "__main__":
    
    
##    inputTable = "C:\\NHGIS\\NHGIS_0008_2010.csv"
##    inputFC = "C:\\NHGIS\\Test.gdb\\Blocks"
##
##    joinTableToFC(inputTable, inputFC, "GISJOIN",
##                        keepFieldsTable=["CM1AA", "CM1AB", "CM1AC", "CM1AD", "CM1AE", "CM1AF", "CM1AG"])

    
##    inputTable = "C:\\PADTACBG\\RawData\\nhgis0035_csv\\nhgis0035_ds172_2010_blck_grp.csv"
##    inputFC = "C:\\PADTACBG\\Analysis\\Analysis.gdb\\NHGIS\\Blockgroups"
##
##    print joinTableToFC(inputTable, inputFC, "GISJOIN", fieldMappings = [["H7V001", "BlockgroupPop"]])

##    inputTable = "C:\\PADTACBG\\RawData\\nhgis0035_csv\\nhgis0035_ds172_2010_block.csv"
##    inputFC = "C:\\PADTACBG\\Analysis\\Analysis.gdb\\NHGIS\\Blocks"
##
##    print joinTableToFC(inputTable, inputFC, "GISJOIN", fieldMappings = [["H7V001", "BlockPop"]])

##    inputTable = "C:\\PADTACBG\\Analysis\\Analysis.gdb\\NHGIS\\Blockgroups"
##    inputFC = "C:\\PADTACBG\\Analysis\\Analysis.gdb\\NHGIS\\Blocks"
##
##    print joinTableToFC(inputTable, inputFC, "Blockgroup", fieldMappings = ["BlockgroupPop"])

    inputFC = "C:\\MasterThesis\\Spring2017\\USA_Analysis_Final\\Analysis.gdb\\NHGIS\\Blockgroups"
    outputFC = "C:\\MasterThesis\\Spring2017\\USA_Analysis_Final\\Analysis.gdb\\NHGIS\\BlockgroupsMDT"
    inputTable = "C:\\MasterThesis\\Spring2017\\NHGIS\\RawExtracts\\nhgis0049_csv\\nhgis0049_ds176_20105_2010_blck_grp_E.csv"

    joinTableToFC(inputTable, inputFC, "GISJOIN", outputFC)
