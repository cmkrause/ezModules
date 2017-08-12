"""Describe various aspects of data sets.

The builtin arcpy.Describe tool is very useful for acquiring information about
a data set.  However, sometimes things that ought to be really simple take
many lines of code to do.  In some other cases, functions that are inherently
describing data are not implemented through the arcpy.Describe function.

The goal of this module is to provide a simpler, more robust module for
describing data sets.
"""
from __future__ import division, print_function
import arcpy, os
from ez.Stats import runningStats
from ez.Python import OrderedSet

def countFeatures(inputOBJ):
    """Returns the count of rows in the specified data set.

    If there is a selection on the specified data set, this count
    reflects the number of selected rows only.

    Why ESRI makes the output of their GetCount_management function [1]
    so un-user-friendly I will never understand, but this function is
    merely a simple wrapper around that.

    Parameter Types:
    inputOBJ - String

    References:
    [1] http://pro.arcgis.com/en/pro-app/tool-reference/data-management/get-count.htm
    """
    
    return int(arcpy.GetCount_management(inputOBJ).getOutput(0))

def listFieldNames(inputOBJ, includeSystemFields = False, types = []):
    """Returns a list of the field names of the specified data set.

    It is very common to want a list of field names of a data set.
    However the output of the arcpy.ListFields function [1] is a list
    of Field objects [2] not simply a list of strings (i.e. the actual
    field names).  This function mitigates that issue and returns a
    list of strings with all the field names within the inputOBJ data set.

    Parameter Types:
    inputOBJ                - String
    includeSystemFields     - Boolean

    Default Parameters:
    includeSystemFields = False
        The default behavior specifies not to return all field names
        that are an "OID" or "Geometry" type.
            
    References:
    [1] http://pro.arcgis.com/en/pro-app/arcpy/functions/listfields.htm
    [2] http://pro.arcgis.com/en/pro-app/arcpy/classes/field.htm
    """
    
    fieldObjects = arcpy.ListFields(inputOBJ)
    fieldNames = []

    for fieldObject in fieldObjects:
        if len(types) == 0:
            if includeSystemFields == True:
                fieldNames.append(fieldObject.name)
            else:
                if fieldObject.type not in ["Geometry", "OID"] and fieldObject.name not in ["Shape_Length", "Shape_Area"]:
                    fieldNames.append(fieldObject.name)
        else:
            if includeSystemFields == True:
                if fieldObject.type in types:
                    fieldNames.append(fieldObject.name)
            else:
                if fieldObject.type not in ["Geometry", "OID"] and fieldObject.name not in ["Shape_Length", "Shape_Area"]:
                    if fieldObject.type in types:
                        fieldNames.append(fieldObject.name)
                    

    return fieldNames

def getFieldObject(inputOBJ, fieldName):
    """Returns an arcpy Field object [1] of the specified field.
    
    In other cases, it is preferable to have an arcpy Field object [1]
    rather than simply a string denoting the field name.  This function
    returns an arcpy Field object [1] for the field in inputOBJ with the
    name specified in fieldName.
    
    Parameter Types:
    inputOBJ    - String
    fieldName   - String
    
    References:
    [1] http://pro.arcgis.com/en/pro-app/arcpy/classes/field.htm
    """
    
    return arcpy.ListFields(inputOBJ, fieldName)[0]

def hasSpatialIndex(inputFC):
    """Determines if the specified feature class has a spatial index.
    
    Spatial indexes can greatly speed up spatial queries [1].
    Creating a spatial index in arcpy is simple [2].
    However, it is wasteful to create a spatial index if it already exists
    since ArcGIS maintains the spatial index automatically.
    
    This function allows you to check for the presence of a spatial index.
    This function returns a Boolean value indicating the presense or absence
    of a spatial index.
    
    Parameter Types:
    inputFC - String
    
    Known Limitations:
    This function works by looking at the name of the indexes and
    comparing them to known names for  spatial indexes of personal and
    file geodatabases [3].  Spatial indexes of shapefiles are different.
    Instead of being named, they are contained in a separate file [4].
    Currently, this function does NOT have the ability to detect the
    presence or absence of the *.sbn shapefile spatial index file.
    Therefore, even if a shapefile does have a spatial index, if you test
    for the presence of the spatial index with this function, it will return False.
    
    References:
    [1] https://msdn.microsoft.com/en-us/library/bb895265.aspx
    [2] http://pro.arcgis.com/en/pro-app/tool-reference/data-management/add-spatial-index.htm
    [3] https://geonet.esri.com/thread/84466
    [4] https://en.wikipedia.org/wiki/Shapefile#Shapefile_spatial_index_format_.28.sbn.29
    """
    
    foundSpatialIndex = False

    desc = arcpy.Describe(statesSHP)

    if desc.dataType == "FeatureClass":
        indexes = arcpy.ListIndexes(inputFC)
        for index in indexes:
            if index.name in ["FDO_Shape", "Shape_Index"]:
                foundSpatialIndex = True

    elif desc.dataType == "ShapeFile":
         spatialIndexFile = "%s.sbn" % desc.catalogPath[:-4]
         if os.path.exists(spatialIndexFile) == True:
             foundSpatialIndex = True

    else:
        raise ValueError("inputFC must be a feature class or shapefile")

    return foundSpatialIndex
        
def hasAttributeIndex(inputOBJ,
                      fieldName = None, indexName = None):
    """Determines if the specified feature class has the specified attribute index.
    
    Attibute indexes can increase querying of a data set.  Before the computationally
    extensive task of creating an attribute index [1] is performed, it would be
    advantageous to see if a similar attribute index exists.  The search can be performed
    by either fieldName or indexName.
    
    Parameter Types:
    inputOBJ    - String
    fieldName   - String
    indexName   - String
    
    Default Parameters:
    fieldName = None
        No field name is provided by default.  This makes this parameter optional
        in the case where searching by indexName is desired.
    indexName = None
        No index name is provided by default.  This makes this parameter optional
        in the case where searching by fieldName is desired.
    
    References:
    [1] http://pro.arcgis.com/en/pro-app/tool-reference/data-management/add-attribute-index.htm
    """
    
    foundAttributeIndex = False
    
    indexes = arcpy.ListIndexes(inputOBJ)
    for index in indexes:
        if fieldName <> None:
            indexFields = index.fields
            for indexField in indexFields:
                if indexField.name == fieldName:
                    foundAttributeIndex = True
        if indexName <> None:
            if index.name == indexName:
                foundAttributeIndex = True

    return foundAttributeIndex

def fieldToNumPyArray(inputOBJ, fieldName,
                      skipNULLs = True):
    """ Returns a NumPy array of a single column of a data set.

    ESRI provides a function to convert a data set to a NumPy array [1].
    Their function is designed to make a multi-dimensional array using the data
    from multiple fields of the data set.
    This function is designed to make a 1-dimensional array using the data
    from a single field of the data set.

    Parameter Types:
    inputOBJ    - String
    fieldName   - String
    skipNULLS   - Boolean

    Default Parameters:
    skipNULLs = True
        Null values will not be returned in the NumPy array

    References:
    [1] http://desktop.arcgis.com/en/arcmap/10.3/analyze/arcpy-data-access/featureclasstonumpyarray.htm
    """

    return arcpy.da.FeatureClassToNumPyArray(inputOBJ, (fieldName, ), skip_nulls = skipNULLs)[fieldName]

def fieldMax(inputOBJ, fieldName,
             method = "NUMPY"):
    """ Returns the maximum value of a field within the specified data set.

    Determining the maximum of a column in a data set is a very common task.
    This function accomplishes this task with one of the following methodologies:
    method = "NUMPY"
        This methodology creates a 1-dimesional NumPy array of the specified field
        in the data set and then uses NumPy to find the maximum of it.
        Advantages of this methodology:
            NumPy is programmed in C (much faster than Python)
        Disadvantages of this methodology:
            The entire field of the data set must be loaded into memory.
            If the data set is large, this may result in Out Of Memory errors.
    method = "CURSOR"
        This methodology is very loosely based on a StackExchange post [1].
        Essentially in this methodology, the field of the data set is iterated
        through row by row and each value is compared to the running maximum.
        If the current row's value is greater than the current running maximum,
        then the running maximum is updated to the current row's value.
        For comparing two values, using an if statement is quicker than using
        the built-in max function [2].
        Advantages of this methodology:
            Since the data set is iterated through row by row, the data set
            is never fully placed in memory and therefore this methodology
            works efficiently even on large data sets.
        Disadvantages:
            Even though this function uses the quicker arcpy.da.SearchCursor [3],
            iterating with Python is not as quick as NumPy's C programming.

    Parameter Types:
    inputOBJ    - String
    fieldName   - String
    method      - String ["NUMPY" or "CURSOR"]

    Default Parameters:
    method = "NUMPY"
        Except with very large datasets that would use lots of memory, creating
        a NumPy array from the field and using numpy to calculate the maximum value
        is probably the quickest method and therefore used as the default

    References:
    [1] http://gis.stackexchange.com/a/101462
    [2] http://www.shocksolution.com/2009/01/optimizing-python-code-for-fast-math/
    [3] http://desktop.arcgis.com/en/arcmap/latest/analyze/arcpy-data-access/searchcursor-class.htm
    """

    if method.upper() == "CURSOR":
        maxValue = None
        cursor = arcpy.da.SearchCursor(inputOBJ, fieldName)
        for row in cursor:
            if maxValue == None:
                maxValue = row[0]
            if row[0] != None:
                if row[0] > maxValue:
                    maxValue = row[0]      
        del cursor
        
    elif method.upper() == "NUMPY":
        array = fieldToNumPyArray(inputOBJ, fieldName)
        maxValue = array.max()
        del array

    else:
        raise ValueError("method must be 'CURSOR' or 'NUMPY'")

    return maxValue

def fieldMin(inputOBJ, fieldName,
             method = "NUMPY"):
    """ Returns the minimum value of a field within the specified data set.

    Determining the minimum of a column in a data set is a very common task.
    This function accomplishes this task with one of the following methodologies:
    method = "NUMPY"
        This methodology creates a 1-dimesional NumPy array of the specified field
        in the data set and then uses NumPy to find the minimum of it.
        Advantages of this methodology:
            NumPy is programmed in C (much faster than Python)
        Disadvantages of this methodology:
            The entire field of the data set must be loaded into memory.
            If the data set is large, this may result in Out Of Memory errors.
    method = "CURSOR"
        This methodology is very loosely based on a StackExchange post [1].
        Essentially in this methodology, the field of the data set is iterated
        through row by row and each value is compared to the running minimum.
        If the current row's value is less than the current running minimum,
        then the running maximum is updated to the current row's value.
        For comparing two values, using an if statement is quicker than using
        the built-in min function [2].
        Advantages of this methodology:
            Since the data set is iterated through row by row, the data set
            is never fully placed in memory and therefore this methodology
            works efficiently even on large data sets.
        Disadvantages:
            Even though this function uses the quicker arcpy.da.SearchCursor [3],
            iterating with Python is not as quick as NumPy's C programming.

    Parameter Types:
    inputOBJ    - String
    fieldName   - String
    method      - String ["NUMPY" or "CURSOR"]

    Default Parameters:
    method = "NUMPY"
        Except with very large datasets that would use lots of memory, creating
        a NumPy array from the field and using numpy to calculate the minimum value
        is probably the quickest method and therefore used as the default

    References:
    [1] http://gis.stackexchange.com/a/101462
    [2] http://www.shocksolution.com/2009/01/optimizing-python-code-for-fast-math/
    [3] http://desktop.arcgis.com/en/arcmap/latest/analyze/arcpy-data-access/searchcursor-class.htm
    """

    if method.upper() == "CURSOR":
        minValue = None
        cursor = arcpy.da.SearchCursor(table, fieldName)
        for row in cursor:
            if minValue == None:
                minValue = row[0]
            if row[0] != None:
                if row[0] < minValue:
                    minValue = row[0]      
        del cursor

    elif method.upper() == "NUMPY":
        array = fieldToNumPyArray(inputOBJ, fieldName)
        minValue = array.min()
        del array

    else:
        raise ValueError("method must be 'CURSOR' or 'NUMPY'")

    return minValue

def fieldMean(inputOBJ, fieldName,
              method = "NUMPY"):
    if method.upper() == "NUMPY":
        return fieldToNumPyArray(inputOBJ, fieldName).mean()
    
    elif method.upper() == "CURSOR":
        valuesCount = 0
        valuesSum   = 0
        
        cursor = arcpy.da.SearchCursor(table, fieldName)
        for row in cursor:
            if row[0] != None:
                valuesCount += 1
                valuesSum   += row[0]
        del cursor
        
        return valuesSum / valuesCount

    else:
        raise ValueError("method must be 'CURSOR' or 'NUMPY'")

def fieldStdDev(inputOBJ, fieldName,
              method = "NUMPY"):
    if method.upper() == "NUMPY":
        return fieldToNumPyArray(inputOBJ, fieldName).std()
    elif method.upper() == "CURSOR":
        stats = runningStats()
        
        cursor = arcpy.da.SearchCursor(table, fieldName)
        for row in cursor:
            if row[0] != None:
                stats.add(row[0])
        del cursor

        return stats.stdDev()
    else:
        raise ValueError("method must be 'CURSOR' or 'NUMPY'")

def fieldSum(inputOBJ, fieldName,
              method = "NUMPY"):
    if method.upper() == "NUMPY":
        return fieldToNumPyArray(inputOBJ, fieldName).sum()
    elif method.upper() == "CURSOR":
        valuesSum = 0
        
        cursor = arcpy.da.SearchCursor(table, fieldName)
        for row in cursor:
            if row[0] != None:
                valuesSum += row[0]
        del cursor
        
        return valuesSum / valuesCount
    else:
        raise ValueError("method must be 'CURSOR' or 'NUMPY'")

def fieldUniqueValues(inputOBJ, fieldName,
                      sort = False, reverse = False, skipNULLs = True):
    if sort == True:
        uniqueValues = set()
    elif sort == False:
        uniqueValues = OrderedSet()

    cursor = arcpy.da.SearchCursor(inputOBJ, fieldName)
    for row in cursor:
        if (skipNULLs == True and row[0] != None) or skipNULLs == False:
            uniqueValues.add(row[0])                  
    del cursor

    uniqueValues = list(uniqueValues)

    if sort == True:
        return sorted(uniqueValues, reverse = reverse)
    else:
        return uniqueValues

def fieldValues(table, fieldName,
                sort = False, reverse = False, skipNULLs = True):
    values = []
    
    cursor = arcpy.da.SearchCursor(table, fieldName)
    for row in cursor:
        if (skipNULLs == True and row[0] != None) or skipNULLs == False:
            values.append(row[0])
    del cursor

    if sort == True:
        return sorted(values, reverse = reverse)
    else:
        return values

if __name__ == "__main__":
    from ez.TestData import statesSHP

    print(statesSHP)
    print("\n\t%s features\n" % countFeatures(statesSHP))

    for fieldName in listFieldNames(statesSHP):
        fieldOBJ = getFieldObject(statesSHP, fieldName)
        print("\tField '%s' is a\t'%s' type" % (fieldName, fieldOBJ.type))

    print("\n\tHas Spatial Index? %s" % hasSpatialIndex(statesSHP))
    if hasSpatialIndex(statesSHP) == False:
        print("\tCreating Spatial Index . . .")
        arcpy.AddSpatialIndex_management(statesSHP)
        print("\tHas Spatial Index? %s" % hasSpatialIndex(statesSHP))

    print("\n\t'GEOID' Field Indexed? %s" % hasAttributeIndex(statesSHP, "GEOID"))
    if hasAttributeIndex(statesSHP, "GEOID") == False:
        print("\tCreating Attribute Index on 'GEOID' field . . .")
        arcpy.AddIndex_management (statesSHP, "GEOID")
        print("\t'GEOID' Field Indexed? %s" % hasAttributeIndex(statesSHP, "GEOID"))

    print("\nThe maximum land area in a state is %s" % fieldMax(statesSHP, "ALAND"))
    print("The minimum land area in a state is %s" % fieldMin(statesSHP, "ALAND"))
    print("The average land area of a state is %s" % fieldMean(statesSHP, "ALAND"))
    print("The standard deviation of land area in the states is %s" % fieldStdDev(statesSHP, "ALAND"))
    print("The total land area of all the states is %s" % fieldSum(statesSHP, "ALAND"))

    print("\nState Names (feature class order):")
    for stateName in fieldValues(statesSHP, "NAME"):
        print("\t%s" % stateName)

    print("\nState Names (alphabetical):")
    for stateName in fieldValues(statesSHP, "NAME", sort = True):
        print("\t%s" % stateName)

    print("\nState Names (reversed alphabetical):")
    for stateName in fieldValues(statesSHP, "NAME", sort = True, reverse = True):
        print("\t%s" % stateName)
