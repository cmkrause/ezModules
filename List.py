import arcpy, os
from ez.Contexts import Environment

def listDatasets(wildcard = None, featureType = None, path = None):
    if path == None:
        if wildcard <> None and featureType <> None:
            return arcpy.ListDatasets(wildcard, featureType)
        elif wildcard == None and featureType <> None:
            return arcpy.ListDatasets(feature_type = featureType)
        elif wildcard <> None and featureType == None:
            return arcpy.ListDatasets(wild_card = wildcard)
    else:
        with Environment("workspace", path):
            if wildcard <> None and featureType <> None:
                datasets = arcpy.ListDatasets(wildcard, featureType)
            elif wildcard == None and featureType <> None:
                datasets = arcpy.ListDatasets(feature_type = featureType)
            elif wildcard <> None and featureType == None:
                datasets = arcpy.ListDatasets(wild_card = wildcard)

        fullPathDatasets = []
        for dataset in datasets:
            fullPathDatasets.append(os.path.join(path, dataset))

        return fullPathDatasets

def listFCs(path):

    return

def listFiles(path):

    return

def listRasters(wildcard = None, rasterType = None, path = None):
    if path == None:
        if wildcard <> None and rasterType <> None:
            return arcpy.ListRasters(wildcard, rasterType)
        elif wildcard == None and rasterType <> None:
            return arcpy.ListRasters(raster_type = rasterType)
        elif wildcard <> None and rasterType == None:
            return arcpy.ListRasters(wild_card = wildcard)
    else:
        with Environment("workspace", path):
            if wildcard <> None and rasterType <> None:
                rasters = arcpy.ListRasters(wildcard, rasterType)
            elif wildcard == None and rasterType <> None:
                rasters = arcpy.ListRasters(raster_type = rasterType)
            elif wildcard <> None and rasterType == None:
                rasters = arcpy.ListRasters(wild_card = wildcard)

        fullPathRasters = []
        for raster in rasters:
            fullPathRasters.append(os.path.join(path, raster))

        return fullPathRasters

def listTables(path):

    return

def listWorkspaces(path):

    return
