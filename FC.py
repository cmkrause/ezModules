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
    else:    
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

def TableToTable(inputTable, outputTable,
                 subsetQuery = None, keepFields = "ALL", omitFields = None, templateOnly = False):
    ## This function is a more capable version of the built-in
    ## Table to Table tool.  For more information
    ## on the original tool, go to
    ## http://pro.arcgis.com/en/pro-app/tool-reference/conversion/feature-class-to-feature-class.htm
    ## TO-DO: Make the templateOnly more efficient (or maybe make a new function)

    outputTableLocation = os.path.dirname(outputTable)
    outputTableName = os.path.basename(outputTable)
    
    if keepFields == "ALL" and omitFields == None:
        if subsetQuery == None:
            arcpy.TableToTable_conversion(inputTable, outputTableLocation, outputTableName)
        else:
            arcpy.TableToTable_conversion(inputTable, outputTableLocation, outputTableName,
                                          where_clause = subsetQuery)
        return True
    else:    
        if keepFields <> "ALL" and omitFields == None:
            
            fieldMappings = arcpy.FieldMappings()
            fieldMappings.addTable(inputTable)

            outputFieldMaps = []

            for keepField in keepFields:
                thisFieldMap = fieldMappings.getFieldMap(fieldMappings.findFieldMapIndex(keepField))
                outputFieldMaps.append(thisFieldMap)

            fieldMappings.removeAll()

            for outputFieldMap in outputFieldMaps:
                fieldMappings.addFieldMap(outputFieldMap)


        if keepFields == "ALL" and omitFields <> None:

            originalFieldNames = listFieldNames(inputTable)
            
            fieldMappings = arcpy.FieldMappings()
            fieldMappings.addTable(inputTable)

            outputFieldMaps = []

            for originalFieldName in originalFieldNames:
                if originalFieldName not in omitFields:
                    thisFieldMap = fieldMappings.getFieldMap(fieldMappings.findFieldMapIndex(originalFieldName))
                    outputFieldMaps.append(thisFieldMap)

            fieldMappings.removeAll()

            for outputFieldMap in outputFieldMaps:
                fieldMappings.addFieldMap(outputFieldMap)

        if subsetQuery == None:
            arcpy.TableToTable_conversion(inputTable, outputTableLocation, outputTableName,
                                          field_mapping = fieldMappings)
        else:
            arcpy.TableToTable_conversion(inputTable, outputTableLocation, outputTableName,
                                          field_mapping = fieldMappings,
                                          where_clause = subsetQuery)

    if templateOnly == True:
        arcpy.DeleteRows_management(outputTable)

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

def createFC(outputFC, geometryType, fields,
             spatialReference = ""):

    outputFCPath = os.path.dirname(outputFC)
    outputFCName = os.path.basename(outputFC)
    
    arcpy.CreateFeatureclass_management(outputFCPath, outputFCName, geometryType,
                                        spatial_reference = spatialReference)

    for field in fields:
        fieldName, fieldType = field
        arcpy.AddField_management(outputFC, fieldName, fieldType)

    return True

def createTable(outputTable, fields):

    outputTablePath = os.path.dirname(outputTable)
    outputTableName = os.path.basename(outputTable)
    
    arcpy.CreateTable_management(outputTablePath, outputTableName)

    for field in fields:
        fieldName, fieldType = field
        arcpy.AddField_management(outputTable, fieldName, fieldType)

    return True

def clearAliases(inputTable):
    fields = listFieldNames(inputTable)
    for field in fields:
        if getFieldObject(inputTable, field).isNullable == True:
            nullability = "NULLABLE"
        else:
            nullability = "NON_NULLABLE"
        arcpy.AlterField_management(inputTable, field, field_is_nullable = nullability, clear_field_alias = "TRUE")
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
