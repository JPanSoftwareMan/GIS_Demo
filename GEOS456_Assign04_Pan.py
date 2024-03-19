#-------------------------------------------------------------------------------
# Name:        Raster Spatial Decision Demonstration
# Purpose:     script can describe raster dataset properties as well as make make calculations for the area of geologic features and watershed areas.
#
# Author:      845942, Justin Pan
#
# Created:     03/21/2023
# Copyright:   (c) SAIT Bachelor of Geographic Information Systems Program
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy
from arcpy.sa import *

class rasterHandler():

    #function describes raster spatial reference and cell size
    def DescribeRasters(self,rasters):
        for raster in rasters:
            # Create a Describe object from the raster dataset
            print("---------------------------------------------")
            print("inspecting raster: ",raster)
            descRaster = arcpy.Describe(raster)

            # Print some raster dataset properties
            print("Raster Format:    %s" % descRaster.format)
            print("Spatial Reference:      %s" % descRaster.spatialReference.name)
            xCount = arcpy.management.GetRasterProperties(raster,"CELLSIZEX").getOutput(0)
            yCount = arcpy.management.GetRasterProperties(raster,"CELLSIZEY").getOutput(0)
            print("cell size x is: ",xCount,"cell size y is: ", yCount)
            print("---------------------------------------------")
            print(arcpy.GetMessages())
    #calculates a raster based on geolgrid and dem query requirements. 
    def conductRasterCalculations2(self,rasters,expressions):
        rasterfinal = []
        print("creating geolgrid and dem query raster")
        for raster,expression in zip(rasters,expressions):
            x = Raster(raster)
            outRaster = eval(expression)
            outRaster.save("{}output".format(raster))

            rasterfinal.append(outRaster)

        finalRaster = CellStatistics(rasterfinal,"SUM","NODATA")
        finalRaster.save("rasterQueried")
        print(arcpy.GetMessages())
        return "rasterQueried"

    
    #creates a zonal statisitcs table based on a raster to calculate statistics on, a zone for the raster to be in, as well as the statistic used to calculate
    #the raster values in the zone. 
    #will differentiate between raster and feature class files for the zone type. 
    def find_watershed_slopesfromDEM(self,slopeRaster,zoneFC,zonefield,zoneValues,outputTblName,statType):
        #create the expression based on zone value
        testExpression = "{} IN({})".format(zonefield,str(zoneValues).replace("[","").replace("]",""))
        print(testExpression)

        #create a describe object to describe the zone feature class.
        desc = arcpy.Describe(zoneFC)
        print(desc.dataType)
        if desc.dataType == "RasterDataset":
            arcpy.management.MakeRasterLayer(zoneFC,"{}_selection".format(zoneFC),where_clause = testExpression)
        #generate zone feature class
        else:
            arcpy.MakeFeatureLayer_management(zoneFC,"{}_selection".format(zoneFC),where_clause = testExpression)
        print(arcpy.GetMessages())
        return ZonalStatisticsAsTable("{}_selection".format(zoneFC),zonefield,slopeRaster,outputTblName,statistics_type=statType)

def main():
    arcpy.CheckOutExtension("Spatial")
    #set workspace and rasters to use.
    arcpy.env.overwriteOutput = True

    #set data path for C drive
    arcpy.env.workspace = r"C:\GEOS456\Assign04\Spatial_Decisions.gdb"
    
    #specify raster to use
    rasters = ["dem","geolgrid"]

    #instantiate the rasterHandler class
    handleRaster = rasterHandler()

    #describe raster properties for dem and geolgrid rasters
    handleRaster.DescribeRasters(rasters)

    #create slope raster
    slopeDEM = Slope("dem","DEGREE")
    slopeDEM.save("slopeDEM")

    #create new raster area which meets all requirements of the client, and generate a zonal statistics table
    finalRasters = ["dem","geolgrid","slopeDEM"]
    expressions = ["(x>=1000) & (x<=1550)","x==7","x<=18"]
    calculatedRaster = handleRaster.conductRasterCalculations2(finalRasters,expressions)
    calculatedRasterTbl = handleRaster.find_watershed_slopesfromDEM("dem",calculatedRaster,"Value",[len(expressions)],"calcRasterStats","MEAN")

    #print results of query area
    with arcpy.da.SearchCursor(calculatedRasterTbl,["COUNT","AREA","MEAN"]) as rasterCursor:
        for row in rasterCursor:
            print("-------------------------------------------")
            print("the area matching the requirements for the dem and geolgrid these properties: ")
            print("cell count: ",row[0])
            print("raster area in sq meters: ",row[1])
            print("mean elevation: ",row[2])
            print("-------------------------------------------")

    #create water table which looks at mean slope of different water sheds and print it.
    watershedFC = "wshds2c"
    watershedField = "WSHDS2C_ID"
    watershedValues = [291,313,525]
    watershedStats = handleRaster.find_watershed_slopesfromDEM(slopeDEM,watershedFC,watershedField,watershedValues,"watershedSlopeStats","MEAN")

    with arcpy.da.SearchCursor(watershedStats,[watershedField,"COUNT","AREA","MEAN"]) as watershedStatsCursor:
        for row in watershedStatsCursor:
            print("-------------------------------------------")
            print("-------------------------------------------")
            print("looking at watershed statistics")
            print("-------------------------------------------")
            print("looking at watershed ID: ",row[0])
            print("cell count: ",row[1])
            print("raster area in sq meters: ",row[2])
            print("mean slope: ",row[3])
            print("-------------------------------------------")


if __name__ == '__main__':
    main()
