import arcpy
from ez.Misc import randomString

def makeFeatureLayer(inputFC, query = None, lyrName = None):
    if lyrName == None:
        lyrName = randomString()
    if query != None:
        arcpy.MakeFeatureLayer_management(inputFC, lyrName, query)
    else:
        arcpy.MakeFeatureLayer_management(inputFC, lyrName)
    return lyrName

## A simple wrapper around arcpy.SelectLayerByAttribute_management
## This wrapper provides a more sensible argument order, a shorter name, and
## the invert option works prior to 10.3
def selectByAttribute(inputLYR, query,
                      selectionType = "NEW_SELECTION", invert = False):
    arcpy.SelectLayerByAttribute_management(inputLYR, selectionType, query)
    if invert == True:
        invertSelection(inputLYR)

## A simple wrapper around arcpy.SelectLayerByLocation_management
## This wrapper provides a shorter name, and the invert option works prior to 10.3
def selectByLocation(inputLYR, overlapType, spatialLYR,
                     searchDistance = None, selectionType = "NEW_SELECTION", invert = False):
    if searchDistance == None:
        arcpy.SelectLayerByLocation_management(inputLYR, overlapType, spatialLYR, selection_type = selectionType)
    else:
        arcpy.SelectLayerByLocation_management(inputLYR, overlapType, spatialLYR, search_distance = searchDistance, selection_type = selectionType)
    if invert == True:
        invertSelection(inputLYR)

def invertSelection(inputLYR):
    arcpy.SelectLayerByAttribute_management(inputLYR, "SWITCH_SELECTION")

def clearSelection(inputLYR):
    arcpy.SelectLayerByAttribute_management(inputLYR, "CLEAR_SELECTION")
