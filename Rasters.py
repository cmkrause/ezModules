import arcpy
from arcpy.sa import *

## This function is a wrapper around the arcpy's built-in Get Raster Properties function
## http://pro.arcgis.com/en/pro-app/tool-reference/data-management/get-raster-properties.htm
## This wrapper will avoid Error 001100: Failed because no statistics is available
## http://support.esri.com/en/technical-article/000011453
## It gets around this error by calculating the statistics first before attempting the
## Get Raster Properties function
## By default, if statistics are already computed, the statistics will not be recomputed
## Of course, the user can overwrite that if they want
def getRasterProperty(raster, rasterProperty, bandIndex = None, skipExistingStats = True):
    if skipExistingStats == True:
        arcpy.CalculateStatistics_management (raster, skip_existing = "SKIP_EXISTING")
    else:
        arcpy.CalculateStatistics_management (raster, skip_existing = "OVERWRITE")

    if bandIndex == None:   
        return arcpy.GetRasterProperties_management(raster, rasterProperty).getOutput(0)
    else:
        return arcpy.GetRasterProperties_management(raster, rasterProperty, bandIndex).getOutput(0)

def rastersOverlap(rasterA, rasterB):
    extentA = arcpy.Describe(rasterA).extent.polygon
    extentB = arcpy.Describe(rasterB).extent.polygon
    if extentA.overlaps(extentB) == True:
        rasterOverlap = CellStatistics ([rasterA, rasterB], "SUM", "NODATA")
        completelyNull = getRasterProperty(rasterOverlap, "ALLNODATA")
        arcpy.Delete_management(rasterOverlap)
        if completelyNull == False:
            return True
        elif completelyNull == True:
            return False
    else:
        return False
