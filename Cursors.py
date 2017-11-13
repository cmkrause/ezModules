import arcpy

def getFields(table, fieldNames, n = 1):
    cursor = arcpy.da.SearchCursor(table, fieldNames)
    if n == 1:
        values = cursor.next()
    elif n != None:
        values = []
        while len(values) < n:
            for row in cursor:
                values.append(row)
    else:
        values = []
        for row in cursor:
            values.append(row)
    del cursor
    return values
