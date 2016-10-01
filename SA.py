import arcpy
import os
from ez.Timer import ezTimer
from ez.FC import createFC

def generateWhereClauses(maxBreak = 120, breakStep = 5, travelDirection = "To"):
    if travelDirection.upper() == "TO":
        fieldName = "ToBreak"
    elif travelDirection.upper() == "FROM":
        fieldName = "FromBreak"
        
    breakValues = range(0, maxBreak, breakStep)

    whereClauses = []
    
    for breakValue in breakValues:
        whereClauses.append("%s > %s AND %s <= %s" % (fieldName, breakValue, fieldName, breakValue + breakStep))

    return whereClauses
        

def makeBreakValuesString(maxBreak, breakStep):
    breakValues = range(0, maxBreak, breakStep)[1:] + [maxBreak]
    # The line below is passed upon
    # http://stackoverflow.com/a/2399122/6214388
    # It is also possible to do the concatenation as shown here
    # http://stackoverflow.com/a/27096484/6214388
    return " ".join(map(str, breakValues))


def generateServiceAreas(facilities, networkDataset, outputFC,
                         maxBreak, breakStep, breakUnits = "Minutes",
                         travelDirection = "To", allowOverlap = True, allowMerge = False,
                         shape = "RINGS", hierachy = True):
    arcpy.CheckOutExtension("Network")
    kwargs = {}
    
    if travelDirection.upper() == "TO":
        kwargs["Travel_Direction"] = "TRAVEL_TO"
    elif travelDirection.upper() == "FROM":
        kwargs["Travel_Direction"] = "TRAVEL_TO"

    if allowMerge == True:
        kwargs["Polygons_for_Multiple_Facilities"] = "MERGE"
    if allowMerge == False:
        kwargs["Polygons_for_Multiple_Facilities"] = "NO_MERGE"
    if allowOverlap == False:
        kwargs["Polygons_for_Multiple_Facilities"] = "NO_OVERLAP"

    if hierachy == True:
        kwargs["Use_Hierarchy_in_Analysis"] = "USE_HIERARCHY"
    elif hierachy == False:
        kwargs["Use_Hierarchy_in_Analysis"] = "NO_HIERARCHY"

    if shape.upper() == "RINGS":
        kwargs["Polygon_Overlap_Type"] = "RINGS"
    elif shape.upper() == "DISKS":
        kwargs["Polygon_Overlap_Type"] = "DISKS"
    
    arcpy.GenerateServiceAreas_na(Facilities = facilities,
                                  Break_Values = makeBreakValuesString(maxBreak, breakStep),
                                  Break_Units = breakUnits,
                                  Network_Dataset = networkDataset,
                                  Service_Areas = outputFC,
                                  **kwargs)
    arcpy.CheckInExtension("Network")
    
def generateVoronoiSAs(facilities, networkDataset,
                       allSAsFC, voronoiSAsFC, facilityDissolvedVoronoiSAsFC,
                       maxBreak = None, breakStep = None, breakUnits = "Minutes",
                       travelDirection = "To", shape = "RINGS", hierachy = True):

    timer = ezTimer(realtimePrint = True)
    if arcpy.Exists(allSAsFC) == False:
        generateServiceAreas(facilities, networkDataset, allSAsFC,
                             maxBreak, breakStep, breakUnits,
                             travelDirection, allowOverlap = True, allowMerge = False,
                             shape = shape, hierachy = hierachy)

    timer.update("Service Areas generated")

    ## The Intersect tool can utilize multiple cores if enabled:
    ## http://pro.arcgis.com/en/pro-app/tool-reference/analysis/intersect.htm
    ## Therefore lets enable it as shown in the documentation:
    ## http://pro.arcgis.com/en/pro-app/tool-reference/environment-settings/parallel-processing-factor.htm
    arcpy.env.parallelProcessingFactor = "100%"

    intersectFC = allSAsFC + "_Intersect"

    arcpy.Intersect_analysis ([allSAsFC], intersectFC, "ALL")

    timer.update("Intersection calculated")

    polygons = {}

    cursor = arcpy.da.SearchCursor(intersectFC, ["SHAPE@WKT", "FacilityID", "FromBreak", "ToBreak"])
    for row in cursor:
        shape, FacilityID, FromBreak, ToBreak = row
        
        if shape not in polygons:
            # The polygon isn't in the polygons dictionary yet, so add it
            polygons[shape] = [FacilityID, FromBreak, ToBreak]
        else:
            # The polygon is already in the polygons dictionary
            
            # If the current FromBreak is the same as the current one in
            # the polygons dictionary, mark it as a tie
            if FromBreak == polygons[shape][1]:
                polygons[shape] = [None, FromBreak, None]
            # If the current FromBreak is smaller than the current one in
            # the polygons dictionary, overwrite it
            if FromBreak < polygons[shape][1]:
                polygons[shape] = [FacilityID, FromBreak, ToBreak]

    del cursor

    timer.update("Finished with SearchCursor")

    ## Create the feature class for the voronoi service areas

    createFC(voronoiSAsFC, "POLYGON", [["FacilityID", "LONG"], ["FromBreak", "DOUBLE"], ["ToBreak", "DOUBLE"]],
             spatialReference = intersectFC)

    timer.update("Voronoi service areas feature class created")

    ## Put the data from the polygons dictionary into the newly created feature class

    cursor = arcpy.da.InsertCursor(voronoiSAsFC, ["SHAPE@WKT", "FacilityID", "FromBreak", "ToBreak"])

    for key, value in polygons.iteritems():
        if value[0] <> None:
            newRow = [key] + value
            cursor.insertRow(newRow)

    del cursor

    timer.update("Finised with InsertCursor")

    ## It is same to delete the intersectFC now that the necessary
    ## has bee inserted into the voronoiSAsFC

    arcpy.Delete_management(intersectFC)

    timer.update("Deleted the temporary intersectFC")

    ## Lastly, dissolve by FacilityID

    arcpy.Dissolve_management(voronoiSAsFC, facilityDissolvedVoronoiSAsFC, ["FacilityID"])

    timer.update("Finished with the dissolve")

    return True

if __name__ == "__main__":

    ## Service Areas test code
    print makeBreakValuesString(120,5)
    print makeBreakValuesString(10,5)


    facilities = os.path.join(os.getcwd(), "Testing.gdb", "MOHospitals")
    networkDataset = "C:/ESRI/streetmap_na/data/streets"
    outputFC = os.path.join(os.getcwd(), "Testing.gdb", "NoOverlapSAs2")

    generateServiceAreas(facilities, networkDataset, outputFC, 120, 120, allowOverlap = False)

    ## Voronoi SA test code

    arcpy.env.overwriteOutput = True
    
    rootFolder  = "C:\\MasterThesis\\PADTACBG\\"
    censusGDB   = os.path.join(rootFolder, "MOSubset.gdb")
    blockgroupsFC = os.path.join(censusGDB, "Blockgroups")
    blocksFC = os.path.join(censusGDB, "BlocksWithPop")
    analysisGDB = os.path.join(rootFolder, "MOHospitals.gdb")
    networkDataset = "C:/ESRI/streetmap_na/data/streets"
    inputFeatures = os.path.join(analysisGDB, "InputFeatures")

    maxBreak = 90
    breakStep = 5

    analysisName = "AllTest"

    allSAsFC                        = os.path.join(analysisGDB, analysisName + "_SAs")
    voronoiSAsFC                    = os.path.join(analysisGDB, analysisName + "_vSAs")
    facilityDissolvedVoronoiSAsFC   = os.path.join(analysisGDB, analysisName + "_fdvSAs") 

    generateVoronoiSAs(inputFeatures, networkDataset,
                       allSAsFC, voronoiSAsFC, facilityDissolvedVoronoiSAsFC,
                       maxBreak, breakStep)
    
