"""Describe various aspects of data sets.

The builtin arcpy.Describe tool is very useful for acquiring information about
a data set.  However, sometimes things that ought to be really simple take
many lines of code to do.  In some other cases, functions that are inherently
descring data are not implemented through the arcpy.Describe function.

The goal of this module is to provide a simpler, more robust module for
describing data sets.
"""

import arcpy

def countFeatures(inputLYR, query=None):
    if query <> None:
        arcpy.SelectLayerByAttribute_management(inputLYR, where_clause = query)
    return int(arcpy.GetCount_management(inputLYR).getOutput(0))

def listFieldNames(inputOBJ, includeSystemFields = False):
    """Returns a list of the field names of the specified data set.

    It is very common to want a list of field names of a data set.
    However the output of the arcpy.ListFields function [1] is a list
    of Field objects [2] not simply a list of strings (i.e. the actual
    field names).  This function mitigates that issue and returns a
    list of strings with all the field names within the inputOBJ data set.

    Parameter Types:
    inputOBJ -- a data set
    includeSystemFields -- Boolean

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
        if includeSystemFields == True:
            fieldNames.append(fieldObject.name)
        else:
            if fieldObject.type not in ["Geometry", "OID"]:
                fieldNames.append(fieldObject.name)

    return fieldNames

def getFieldObject(inputOBJ, fieldName):
    """Returns an arcpy Field object [1] of the specified field.
    
    In other cases, it is preferable to have an arcpy Field object [1]
    rather than simply a string denoting the field name.  This function
    returns an arcpy Field object [1] for the field in inputOBJ with the
    name specified in fieldName.
    
    Parameter Types:
    inputOBJ -- a data set
    fieldName -- String
    
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
    inputFC - a feature class in a file or personal geodatabase
    
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
    
    indexes = arcpy.ListIndexes(inputFC)
    for index in indexes:
        if index.name in ["FDO_Shape", "Shape_Index"]:
            foundSpatialIndex = True

    return foundSpatialIndex
        

def hasAttributeIndex(inputOBJ,
                      fieldName = None, indexName = None):
    """Determines if the specified feature class has the specified attribute index.
    
    Attibute indexes can increase querying of a data set.  Before the computationally
    extensive task of creating an attribute index [1] is performed, it would be
    advantageous to see if a similar attribute index exists.  The search can be performed
    by either fieldName or indexName.
    
    Parameter Types:
    inputOBJ - a data set
    fieldName - String
    indexName - String
    
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

if __name__ == "__main__":
    import os
    inputSHP = os.path.join(os.getcwd(), "testData", "Counties.shp")
    print listFieldNames(inputSHP)
    print hasSpatialIndex(inputSHP)
    print hasSpatialIndex("C:\\NHGIS\\NHGIS2010.gdb\\Blocks")
    print hasAttributeIndex("C:\\NHGIS\\NHGIS2010.gdb\\Blocks", indexName = "FDO_OBJECTID")
