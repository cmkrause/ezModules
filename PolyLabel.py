from __future__ import division
from math import sqrt
import arcpy
from ez.Misc import randomString, frange
from ez.Describe import fieldMin

## This is an arcpy adaptation of MapBox's PolyLabel algorithm
## Their algorithm was developed to efficently find the visual center of a polygon
## See their initial blog post about the algorithm at:
## https://blog.mapbox.com/a-new-algorithm-for-finding-a-visual-center-of-a-polygon-7c77e6492fbc
## They also provide their algorithm in C++ and JavaScript on their GitHub page:
## https://github.com/mapbox/polylabel
## This is not the first Python implemementation (see [1] and [2])
## nor is it the first arcpy implementation (see [3] and [4])
## However, it is the first I have seen that out-of-the-box will calculate
## the visual centers for every feature in a feature class (see polyLabelFC function)
## Despite Python having an implementation of PriorityQueues, they were not used
## because I found it simpler to before the sorting on a list using a lambda than
## modifying the data structures (see [1] and [2]) to accomodate how PriorityQueue sorts (see [5])

## [1] https://github.com/Twista/python-polylabel
## [2] https://github.com/Justin-Kuehn/polylabel-py
## [3] https://darrenwiens.wordpress.com/2016/08/17/mapbox-visual-center-algorithm-arcpy/
## [4] https://darrenwiens.wordpress.com/2016/08/19/mapbox-visual-center-algorithm-arcpy-attempt-2/
## [5] https://stackoverflow.com/questions/9289614/how-to-put-items-into-priority-queues

def polyLabelFC(inputFC, outputFC, precision = None):
	origOIDFieldName = randomString(10)	
	arcpy.AddField_management(inputFC, origOIDFieldName, "LONG")
	
	polyLabels = {}
	
	if precision == None:
		precision = sqrt(fieldMin(inputFC, "SHAPE@AREA")) / 2
	
	cursor = arcpy.da.UpdateCursor(inputFC, ["OID@", "SHAPE@", origOIDFieldName])
	for oid, shape, origOID in cursor:
		cursor.updateRow([oid, shape, oid])
		polyLabels[oid] = polyLabelPolygon(shape, precision)
	del cursor
			
	arcpy.FeatureToPoint_management(inputFC, outputFC)
	arcpy.DeleteField_management(inputFC, origOIDFieldName)
	
	cursor = arcpy.da.UpdateCursor(outputFC, [origOIDFieldName, "SHAPE@"])
	for origOID, shape in cursor:
		cursor.updateRow([origOID, polyLabels[origOID]])
	del cursor
	
	arcpy.DeleteField_management(outputFC, origOIDFieldName)
	
def polyLabelPolygon(polygon, precision = 1):
	extent = polygon.extent
	minX, minY, maxX, maxY = extent.XMin, extent.YMin, extent.XMax, extent.YMax
	width, height = extent.width, extent.height
	cellSize = min(width, height)
	h = cellSize / 2
	
	cellQueue = []
	
	if cellSize == 0:
		return arcpy.Point(minX, minY)
		
	for x in frange(minX, maxX, cellSize):
		for y in frange(minY, maxY, cellSize):
			cellQueue.append(Cell(x + h, y + h, h, polygon))
	
	bestCell = getCentroidCell(polygon)
	
	bboxCell = Cell(minX + width / 2, minY + height / 2, 0, polygon)
	if bboxCell.d > bestCell.d:
		bestCell = bboxCell
		
	while len(cellQueue) > 0:
		cellQueue.sort(key = lambda cell: cell.max)         
		cell = cellQueue.pop() 
		
		if cell.d > bestCell.d:
			bestCell = cell
			
		if (cell.max - bestCell.d) <= precision:
			continue
			
		h = cell.h / 2
		cellQueue.append(Cell(cell.x - h, cell.y - h, h, polygon));
		cellQueue.append(Cell(cell.x + h, cell.y - h, h, polygon));
		cellQueue.append(Cell(cell.x - h, cell.y + h, h, polygon));
		cellQueue.append(Cell(cell.x + h, cell.y + h, h, polygon));

	return arcpy.Point(bestCell.x, bestCell.y)
		
def getCentroidCell(polygon):
	centroid = polygon.centroid
	return Cell(centroid.X, centroid.Y, 0, polygon)

class Cell:
    def __init__(self, x, y, h, polygon):
        self.x = x
        self.y = y
        self.h = h
        self.d = pointToPolygonDistance(x, y, polygon)
        self.max = self.d + self.h * math.sqrt(2)

def pointToPolygonDistance(x, y, polygon):
	returnTuple = polygon.boundary().queryPointAndDistance(arcpy.Point(x, y))
	if returnTuple[3] == True:
		return returnTuple[2]
	elif returnTuple[3] == False:
		return -1 * returnTuple[2]
		
if __name__ == "__main__":

	from ez.Timer import ezTimer

	timer = ezTimer()
	for precision in sorted(range(1000, 11000, 1000), reverse = True):
		print "Precision = %s" % precision
		inputFC = "D:\\PolyLabel\\Test.gdb\\Lower48"
		outputFC = "in_memory\\Lower48Labels_%s" % precision
		polyLabelFC(inputFC, outputFC, precision)
		timer.update("Precision = %s" % precision)
	
	timer.report()