import arcpy
from arcpy.sa import *
from ez.Contexts import Extension, Environment

## This function is a wrapper around the arcpy's built-in Get Raster Properties function
## http://pro.arcgis.com/en/pro-app/tool-reference/data-management/get-raster-properties.htm
## This wrapper will avoid Error 001100: Failed because no statistics is available
## http://support.esri.com/en/technical-article/000011453
## It gets around this error by calculating the statistics first before attempting the
## Get Raster Properties function
## By default, if statistics are already computed, the statistics will not be recomputed
## Of course, the user can overwrite that if they want
## Inconveniently, the results directly from the Get Raster Properties function are unicode strings
## https://gis.stackexchange.com/questions/55246/casting-arcpy-result-as-integer-instead-arcpy-getcount-management
## This function returns the values in the appropriate formats (int, float, etc.) based on which
## property was requested
def getRasterProperty(raster, rasterProperty, bandIndex = None, skipExistingStats = True):

    rasterProperty = rasterProperty.upper()
    
    if skipExistingStats == True:
        arcpy.CalculateStatistics_management (raster, skip_existing = "SKIP_EXISTING")
    else:
        arcpy.CalculateStatistics_management (raster, skip_existing = "OVERWRITE")

    if bandIndex == None:   
        returnValue = arcpy.GetRasterProperties_management(raster, rasterProperty).getOutput(0)
    else:
        returnValue = arcpy.GetRasterProperties_management(raster, rasterProperty, bandIndex).getOutput(0)

    if rasterProperty in ["UNIQUEVALUECOUNT", "VALUETYPE", "COLUMNCOUNT", "ROWCOUNT", "BANDCOUNT"]:
        return int(returnValue)
    elif rasterProperty in ["MINIMUM", "MAXIMUM", "MEAN", "STD", "TOP", "LEFT", "RIGHT", "BOTTOM", "CELLSIZEX", "CELLSIZEY"]:
        returnValue = float(returnValue)
        if returnValue.is_integer() == True:
            return int(returnValue)
        else:
            return returnValue
    elif rasterProperty in ["ANYNODATA", "ALLNODATA"]:
        return bool(int(returnValue))
    else:
        return str(returnValue)

def rastersOverlap(rasterA, rasterB, extentsOnly = False):
    ## Using the built-in .overlaps() function on an arcpy Extent object seems to be broken
    ## Since we are only comparing the extents, comparing their bounds numerically is trivial
    ## The function below does just that
    def extentOverlap(extentA, extentB):
        ## The function below was inspired from
        ## https://nedbatchelder.com/blog/201310/range_overlap_in_two_compares.html
        def rangeOverlap(startA, endA, startB, endB):
            return endA >= startB and endB >= startA
        return rangeOverlap(extentA.XMin, extentA.XMax, extentB.XMin, extentB.XMax) and \
               rangeOverlap(extentA.YMin, extentA.YMax, extentB.YMin, extentB.YMax)

    extentA = arcpy.Describe(rasterA).extent
    extentB = arcpy.Describe(rasterB).extent
    if extentsOnly == True:
        return extentOverlap(extentA, extentB)
    else:
        if extentOverlap(extentA, extentB) == True:
            with Extension("Spatial"), Environment("scratchWorkspace", "in_memory"):
                rasterOverlap = CellStatistics ([rasterA, rasterB], "SUM", "NODATA")
                completelyNull = getRasterProperty(rasterOverlap, "ALLNODATA")
                arcpy.Delete_management(rasterOverlap)

            if completelyNull == False:
                return True
            elif completelyNull == True:
                return False
        else:
            return False
