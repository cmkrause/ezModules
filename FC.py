import arcpy
import os
from ez.Describe import *

def FCToFC(inputFC, outputFC,
           subsetQuery = None, keepFields = "ALL", omitFields = None):
    ## This function is a more capable version of the built-in
    ## Feature Class to Feature Class tool.  For more information
    ## on the original tool, go to
    ## http://pro.arcgis.com/en/pro-app/tool-reference/conversion/feature-class-to-feature-class.htm

    outputFCLocation = os.path.dirname(outputFC)
    outputFCName = os.path.basename(outputFC)
    
    if keepFields == "ALL" and omitFields == None:
        if subsetQuery == None:
            arcpy.FeatureClassToFeatureClass_conversion(inputFC, outputFCLocation, outputFCName)
        else:
            arcpy.FeatureClassToFeatureClass_conversion(inputFC, outputFCLocation, outputFCName,
                                                        where_clause = subsetQuery)
        return True
        
    if keepFields <> "ALL" and omitFields == None:
        
        fieldMappings = arcpy.FieldMappings()
        fieldMappings.addTable(inputFC)

        outputFieldMaps = []

        for keepField in keepFields:
            thisFieldMap = fieldMappings.getFieldMap(fieldMappings.findFieldMapIndex(keepField))
            outputFieldMaps.append(thisFieldMap)

        fieldMappings.removeAll()

        for outputFieldMap in outputFieldMaps:
            fieldMappings.addFieldMap(outputFieldMap)


    if keepFields == "ALL" and omitFields <> None:

        originalFieldNames = listFieldNames(inputFC)
        
        fieldMappings = arcpy.FieldMappings()
        fieldMappings.addTable(inputFC)

        outputFieldMaps = []

        for originalFieldName in originalFieldNames:
            if originalFieldName not in omitFields:
                thisFieldMap = fieldMappings.getFieldMap(fieldMappings.findFieldMapIndex(originalFieldName))
                outputFieldMaps.append(thisFieldMap)

        fieldMappings.removeAll()

        for outputFieldMap in outputFieldMaps:
            fieldMappings.addFieldMap(outputFieldMap)

    if subsetQuery == None:
        arcpy.FeatureClassToFeatureClass_conversion(inputFC, outputFCLocation, outputFCName,
                                                    field_mapping = fieldMappings)
    else:
        arcpy.FeatureClassToFeatureClass_conversion(inputFC, outputFCLocation, outputFCName,
                                                    field_mapping = fieldMappings,
                                                    where_clause = subsetQuery)

    return True

def copyFieldsToFC(inputOBJ, outputFC, fieldsToCopy):
    ## This only recreates the fields by name and type.
    ## This does NOT copy any data or do any type of join.
    for fieldToCopy in fieldsToCopy:
        templateField = getFieldObject(inputOBJ, fieldToCopy)
        ## http://pro.arcgis.com/en/pro-app/tool-reference/data-management/add-field.htm
        arcpy.AddField_management(outputFC, templateField.name, templateField.type, templateField.precision,
                                  templateField.scale, templateField.length, templateField.aliasName,
                                  templateField.isNullable, templateField.required, templateField.domain)
    return True

if __name__ == "__main__":
    arcpy.env.workspace = os.path.join(os.getcwd(), "testData")
    arcpy.env.overwriteOutput = True

    inputSHP = os.path.join(arcpy.env.workspace, "Counties.shp")
    
    outputSHP = os.path.join(arcpy.env.workspace, "CountiesAll.shp")
    FCToFC(inputSHP, outputSHP)
    print "%s created" % outputSHP
    
    outputSHP = os.path.join(arcpy.env.workspace, "CountiesPop.shp")
    FCToFC(inputSHP, outputSHP, keepFields = ["GEOID10", "NAMELSAD10", "DP0010001"])
    print "%s created" % outputSHP

    outputSHP = os.path.join(arcpy.env.workspace, "CountiesNoName.shp")
    FCToFC(inputSHP, outputSHP, omitFields = ["NAMELSAD10"])
    print "%s created" % outputSHP

    outputSHP = os.path.join(arcpy.env.workspace, "CountiesLarge.shp")
    FCToFC(inputSHP, outputSHP, '"DP0010001" >= 100000')
    print "%s created" % outputSHP
