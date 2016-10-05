## The original reason for creating this module was to faciliate
## the use of a GROUP BY clause using SQLite.
## Using DB Browser for SQLite, I was able to get the expected results.
## However, when running the exact same query in Python, I got different
## results (incorrect responses).  After some digging around, I found
## older versions of SQLite do not run the code as expected:
## http://stackoverflow.com/a/13931840
## DB Browser for SQLite was running a nearly current version of SQLite.
## To check the version of SQLite included with Python, I followed this:
## http://stackoverflow.com/a/20910053
## Alas Python 2.7 ships with a 2009 version of SQLite.
## To get the expected results, I need at least version 3.7.11
## After several failed attempts, I was able to upgrade the version of
## SQLite used by Python following the steps described here:
## http://www.obsidianforensics.com/blog/upgrading-python-sqlite

import arcpy
import os
import sqlite3
from ez.Misc import cleanseString
from ez.FC import createTable

## SQLite can perform much more complex/powerful SQL than the querying
## allowed within ArcGIS.  This function will convert a table into a SQLite
## database that can be queried however you see fit.
## For example of where the internal SQL is looking, look here:
## http://support.esri.com/technical-article/000008936
## This function was VERY loosely inspired by this presentation:
## http://www.scaug.org/Resources/REGIONAL/CONFERENCES/2013_ADDISON_SCAUG_CONFERENCE/Presentations/SQLite.pdf
## After creating this function, I found a similar methodology proposed here:
## http://gis.stackexchange.com/a/166866
## Rather than using a cursor to load the data, it is much quicker to have
## the Data Access module create a NumPy Array:
##http://pro.arcgis.com/en/pro-app/arcpy/data-access/tabletonumpyarray.htm
def tableToSQLite(inputTable, fields, outputDB,
                  outputTableName = None, overwrite = False):
    
    ## If outputTableName was not specified, use the name of the inputTable
    if outputTableName == None:
        outputTableName = os.path.basename(inputTable)
    
    ## Get the data from the table
    numpyArray = arcpy.da.TableToNumPyArray(inputTable, fields)
    pyList = numpyArray.tolist()

    ## Establish a SQLite connection
    conn = sqlite3.connect(outputDB)

    ## --------------------------------------------------
    ## This section concatenates all the necessary pieces
    ## to make strings for the CREATE and INSERT statements
    ## with the same form as shown in the documentation:
    ## https://docs.python.org/2/library/sqlite3.html#using-shortcut-methods

    sqlCreateString = "create table %s (" % outputTableName
    sqlInsertString = "insert into %s (" % outputTableName
    
    fieldNumber = 0
    for field in fields:
        ## Figure out the Python -> SQLite data types based upon
        ## https://docs.python.org/2/library/sqlite3.html#sqlite-and-python-types
        pyFieldType = type(pyList[0][fieldNumber])
        if pyFieldType == int or pyFieldType == long:
            sqlFieldType = "INTEGER"
        if pyFieldType == float:
            sqlFieldType = "REAL"
        if pyFieldType == str or pyFieldType == unicode:
            sqlFieldType = "TEXT"
        
        sqlCreateString += "%s %s, " % (cleanseString(field), sqlFieldType)

        sqlInsertString += "%s, " % cleanseString(field)
        
        fieldNumber += 1

    sqlCreateString = sqlCreateString[:-2] + ")"

    sqlInsertString = sqlInsertString[:-2] + ") values ("
    for i in xrange(len(fields)):
        sqlInsertString += "?, "

    sqlInsertString = sqlInsertString[:-2] + ")"

    ## That's all for this section.
    ## --------------------------------------------------

    ## If overwrite is set to True, try to DROP the existing table
    if overwrite == True:
        sqlDropString = "drop table if exists %s" % outputTableName
        conn.execute(sqlDropString)

    ## CREATE the table for the data to be stored
    conn.execute(sqlCreateString)

    ## INSERT the data into the table
    conn.executemany(sqlInsertString, pyList)

    ## Save and close
    conn.commit()
    conn.close()

    return True

def SQLiteQueryToTable(inputDB, dbQuery, outputTable, fields,
                       overwrite = False):

    ## Potentially implement something to extract the field names like this:
    ## http://stackoverflow.com/a/7831685

    ## Change the env.overwriteOutput variable (if the user requested it)
    if overwrite == True:
        initialenvOverwriteOutput = arcpy.env.overwriteOutput
        arcpy.env.overwriteOutput = True

    ## Create the table to hold the results of the SQL query
    createTable(outputTable, fields)

    ## Now establish an insert cursor for the table
    insertCursorFields = []

    for field in fields:
        fieldName, fieldType = field
        insertCursorFields.append(fieldName)

    insertCursor = arcpy.da.InsertCursor(outputTable, insertCursorFields)
        
    ## Establish a SQLite connection
    conn = sqlite3.connect(inputDB)


    ## Iterate through the results of the SQL query
    ## and insert each row into the newly created table

    for row in conn.execute(dbQuery):
        insertCursor.insertRow(row)

    ## Close the connection without saving (no changes were made anyway)
    conn.close()

    ## Reset the env.overwriteOutput back to how it was originally
    if overwrite == True:
        arcpy.env.overwriteOutput = arcpy.env.overwriteOutput

    return True

class SQLiteWrapper:
    def __init__(self, DB, debugOn = False):
        self.Connection = sqlite3.connect(DB)
        self.Connection.row_factory = sqlite3.Row
        self.Cursor = self.Connection.cursor()
        self.debugOn = debugOn
        
    def execSQL(self, query, **kwargs):
        self.debugCheck(query, kwargs)
        self.Cursor.execute(query)
        self.Connection.commit()
        
    def returnAll(self, query, **kwargs):
        self.debugCheck(query, kwargs)
        self.execSQL(query)
        return self.Cursor.fetchall()
    
    def returnOne(self, query, **kwargs):
        self.debugCheck(query, kwargs)
        self.execSQL(query)
        return self.Cursor.fetchone()
    
    def returnValue(self, query, **kwargs):
        self.debugCheck(query, kwargs)
        self.execSQL(query)
        return self.Cursor.fetchone()[self.Cursor.description[0][0]]
    
    def returnN(self, query, N, **kwargs):
        self.debugCheck(query, kwargs)
        self.execSQL(query)
        return self.Cursor.fetchall()[:N]
    
    def lastID(self):
        return self.Cursor.lastrowid
    
    def debugCheck(self, query, keys):
        printedQuery = False
        for key in keys:
            if key == "debug":
                if keys[key] == True:
                    print query
                    printedQuery = True
        if self.debugOn == True and printedQuery == False:
            print query

if __name__ == "__main__":

    rootFolder  = "C:\\MasterThesis\\PADTACBG\\"
    analysisGDB = os.path.join(rootFolder, "MOHospitals.gdb")
    inputFeatures = os.path.join(analysisGDB, "SumStats2_AllHospitals2")

    outputDB = "C:\\MasterThesis\\PADTACBG\\test.db"

##    tableToSQLite(inputFeatures, ["OID@", "BLOCKGROUP", "FacilityID", "SUM_PartialAverage"], outputDB,
##                  "temp_table2", overwrite = True)

    sql = "select BLOCKGROUP, FacilityID, min(SUMPartialAverage) from temp_table2 group by BLOCKGROUP"

    outputTable = os.path.join(analysisGDB, "FinalResults")

    SQLiteQueryToTable(outputDB, sql, outputTable, [["BLOCKGROUP", "TEXT"], ["FacilityID", "LONG"], ["TravelTime", "DOUBLE"]],
                       overwrite = True)



