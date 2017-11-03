import arcpy, os
from ez.Contexts import Environment
from arcpy import env

## Need to handle the case where env.workspace is not set and
## path == None

def listDatasets(wildcard = None, featureType = None, path = None):
    if path == None:
        if wildcard <> None and featureType <> None:
            return arcpy.ListDatasets(wildcard, featureType)
        elif wildcard == None and featureType <> None:
            return arcpy.ListDatasets(feature_type = featureType)
        elif wildcard <> None and featureType == None:
            return arcpy.ListDatasets(wild_card = wildcard)
        elif wildcard == None and featureType == None:
            return arcpy.ListDatasets()
    else:
        with Environment("workspace", path):
            if wildcard <> None and featureType <> None:
                datasets = arcpy.ListDatasets(wildcard, featureType)
            elif wildcard == None and featureType <> None:
                datasets = arcpy.ListDatasets(feature_type = featureType)
            elif wildcard <> None and featureType == None:
                datasets = arcpy.ListDatasets(wild_card = wildcard)
            elif wildcard == None and featureType == None:
                datasets = arcpy.ListDatasets()

        fullPathDatasets = []
        for dataset in datasets:
            fullPathDatasets.append(os.path.join(path, dataset))

        return fullPathDatasets

def listFeatureClasses(wildcard = None, featureType = None, path = None):
    if path == None:
        if arcpy.Describe(env.workspace).dataType == "FeatureDataset":
            path = os.path.dirname(env.workspace)
            featureDataset = os.path.basename(env.workspace)
            kwargs = {"feature_dataset":featureDataset}
        else:
            featureDataset = None
            kwargs = {}
            
        with Environment("workspace", path):
            if wildcard <> None and featureType <> None:
                featureClasses = arcpy.ListFeatureClasses(wildcard, featureType, **kwargs)
            elif wildcard == None and featureType <> None:
                featureClasses = arcpy.ListFeatureClasses(feature_type = featureType, **kwargs)
            elif wildcard <> None and featureType == None:
                featureClasses = arcpy.ListFeatureClasses(wild_card = wildcard, **kwargs)
            elif wildcard == None and featureType == None:
                featureClasses = arcpy.ListFeatureClasses(**kwargs)

        return featureClasses
    else:
        if arcpy.Describe(path).dataType == "FeatureDataset":
            featureDataset = os.path.basename(path)
            path = os.path.dirname(path)
            kwargs = {"feature_dataset":featureDataset}
        else:
            featureDataset = None
            kwargs = {}

        with Environment("workspace", path):
            if wildcard <> None and featureType <> None:
                featureClasses = arcpy.ListFeatureClasses(wildcard, featureType, **kwargs)
            elif wildcard == None and featureType <> None:
                featureClasses = arcpy.ListFeatureClasses(feature_type = featureType, **kwargs)
            elif wildcard <> None and featureType == None:
                featureClasses = arcpy.ListFeatureClasses(wild_card = wildcard, **kwargs)
            elif wildcard == None and featureType == None:
                featureClasses = arcpy.ListFeatureClasses(**kwargs)

        fullPathFeatureClasses = []
        for featureClass in featureClasses:
            if featureDataset == None:
                fullPathFeatureClasses.append(os.path.join(path, featureClass))
            else:
                fullPathFeatureClasses.append(os.path.join(path, featureDataset, featureClass))

        return fullPathFeatureClasses
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
        elif wildcard == None and rasterType == None:
            return arcpy.ListRasters()
    else:
        with Environment("workspace", path):
            if wildcard <> None and rasterType <> None:
                rasters = arcpy.ListRasters(wildcard, rasterType)
            elif wildcard == None and rasterType <> None:
                rasters = arcpy.ListRasters(raster_type = rasterType)
            elif wildcard <> None and rasterType == None:
                rasters = arcpy.ListRasters(wild_card = wildcard)
            elif wildcard == None and rasterType == None:
                rasters = arcpy.ListRasters()

        fullPathRasters = []
        for raster in rasters:
            fullPathRasters.append(os.path.join(path, raster))

        return fullPathRasters

def listTables(path):

    return

def listWorkspaces(path):

    return
