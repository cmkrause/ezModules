import os
from ez.Internet import hasInternet, downloadFile
from ez.Python import extractZipFile, listFiles

rootFolder = os.path.dirname(__file__)

if hasInternet() == True:

    statesURL = "http://www2.census.gov/geo/tiger/GENZ2016/shp/cb_2016_us_state_20m.zip"
    statesZIP = os.path.join(rootFolder, os.path.basename(statesURL))

    if os.path.exists(statesZIP) == False:
        downloadFile(statesURL, rootFolder)
        extractZipFile(statesZIP, rootFolder)

    statesSHP = listFiles(rootFolder, "*.shp")[0]
