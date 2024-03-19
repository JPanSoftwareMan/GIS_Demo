#-------------------------------------------------------------------------------
# Name:        Cypress Hlls Provincial Park Pipeline Construction
# Purpose:     A script for finding the best route for the construction of a hypothetical pipeline through Cypress Hills Provincial Park.
#
# Author:      845942, Justin Pan
#
# Created:     03/21/2023
# Copyright:   (c) SAIT Bachelor of Geographic Information Systems Program
# Licence:     <your licence>
#-------------------------------------------------------------------------------
import arcpy
import os
import time
from arcpy.sa import *
from arcpy import env
import arcpy.mp as MAP



class FinalProjectClass():

    def __init__(self,outputGDBName,outputFolderPath,startPointFC,endPointFC,studyAreaPoly):
        #output gdb params
        self.outGDBname = outputGDBName
        self.outputFolder = outputFolderPath
        self.fulloutputGDB = os.path.join(self.outputFolder, self.outGDBname + ".gdb")

        #stores feature datasets on creation
        self.pointFD = ""
        self.polygonFD = ""
        self.lineFD = ""

        #set start point and end point data fc's.
        self.StartPoint = startPointFC
        self.endPoint = endPointFC

        #set study area polygon
        self.studyArea =studyAreaPoly
        self.studyAreaSet = ""


        #store coord system
        self.outputSR = "NAD 1983 UTM Zone 12N"
        self.outputDatum = "GCS_North_American_1983"

        #store river and road FCs
        self.riverFC = ""
        self.roadsFC = ""


        #store NTS50 FC
        self.NTS50 = ""

        #store the raw DEM and Land cover rasters
        self.DEM = ""
        self.LandcoverR = ""
        self.slopeDEM = ""
        self.Riverbuffer = ""
        self.roadBuffer = ""

        #store outputs of reclassification
        self.slopeClassified = ""
        self.landcoverClassified = ""
        self.riversClassified =""
        self.roadsClassified = ""

        #store remap values for each reclassification
        self.slopeRemap = [[0,3.9999,1],[4,10,2],[10,9999,3]]
        self.Landcoverremap = [[1,3],[2,1],[3,1],[4,1],[5,2],[7,3]]
        self.riverRemap =[[0,49.999,3],[50,250,2],[250,9999,1]]
        self.roadRemap =[[0,29.9999,1],[30,250,2],[250,9999,3]]


        self.totalCostSurface = ""

        self.pipelineVector = ""
    #checks if process was successfully completed
    def checkSuccessStatus(self):
        print("success status: ")
        print(arcpy.GetMessages())
        print("---------------------------------------------")


    #check if gdb from previous run exists, if it does, delete it, and create the gdb again.
    def setoutputGDB(self):
        if arcpy.Exists(self.fulloutputGDB):
            print("deleting previously created gdb")
            arcpy.Delete_management(self.fulloutputGDB)
        print("creating new output gdb")
        self.checkSuccessStatus()
        return arcpy.management.CreateFileGDB(self.outputFolder, self.outGDBname)

    #set feature datasets
    def setFDs(self):
        self.pointFD = arcpy.management.CreateFeatureDataset(self.fulloutputGDB,"Points",arcpy.SpatialReference(self.outputSR))
        self.polygonFD = arcpy.management.CreateFeatureDataset(self.fulloutputGDB,"Polygons",arcpy.SpatialReference(self.outputSR))
        self.lineFD = arcpy.management.CreateFeatureDataset(self.fulloutputGDB,"Lines",arcpy.SpatialReference(self.outputSR))
        self.checkSuccessStatus()

    #set study area
    def setStudyArea(self):
        self.studyAreaSet = self.projectFC(self.studyArea,"StudyArea",self.polygonFD,self.outputSR,self.outputDatum)
        self.checkSuccessStatus()


    #check feature class or shp to see if it is in the right coord system.
    def projectFC(self,FC,FC_outputName,outputWorkspace,outCoordSystem,outDatum):
        desc = arcpy.Describe(FC)
        spatialRef = desc.spatialReference
        print("check coordinate system of FC ",FC)
        #if feature coord system is unknown, shut program down and alert user.
        #If feature coordinate system is known check if it matches. If not, project it.
        if spatialRef.name  == "Unknown":
            print("error! Coordinate system of FC {},is unknown".format(FC), " please give it a coord system and try again")
            exit()
        elif spatialRef.name != "Unknown" and spatialRef.name != outDatum:
            print("changing datum to: {}".format(outDatum))
            return arcpy.management.Project(FC,str(outputWorkspace) + "\\{}".format(FC_outputName),arcpy.SpatialReference("NAD 1983 UTM Zone 12N"))
        elif(spatialRef.name  != outCoordSystem and spatialRef.name  == outDatum):
            print("The FC coordinate system has the correct datum, but is not projected yet. Projecting into the {} planar coordinate system".format(outCoordSystem))
            return arcpy.management.Project(FC,str(outputWorkspace) + "\\{}".format(FC_outputName),arcpy.SpatialReference("NAD 1983 UTM Zone 12N"))
        elif spatialRef.name  == outCoordSystem:
            print("doing import with no projecting needed")
        else:
            print("the datum is incorrect, please check the fc")
        self.checkSuccessStatus()

    #imports point features
    def importPointFeatures(self):
        startPointCopy = arcpy.conversion.ExportFeatures(self.StartPoint,str(self.fulloutputGDB) + "\\StartP_copy","""UFI = 'A21605053'""")
        endPointCopy = arcpy.conversion.ExportFeatures(self.endPoint,str(self.fulloutputGDB)+"\\End_P_copy","""UWID = '0074013407000'""")

        print("creating start and end points")
        self.StartPoint = self.projectFC(startPointCopy,"start",self.pointFD,self.outputSR,self.outputDatum)
        self.endPoint = self.projectFC(endPointCopy,"end",self.pointFD,self.outputSR,self.outputDatum)

        arcpy.Delete_management(startPointCopy)
        arcpy.Delete_management(endPointCopy)
        self.checkSuccessStatus()

    #imports line features and creates classified rasters from them.
    def importLineFeatures(self,workspace):
        walk = arcpy.da.Walk(workspace, datatype="FeatureClass", type="Polyline")
        for dirpath, dirnames, filenames in walk:
            for filename in filenames:
                fullPath = os.path.join(dirpath, filename)
                print(filename)

                if ".gdb" not in filename and ".gdb" not in dirpath and ".gdb" not in dirnames:
                    #import roads and river feature classes. Then assign them to the roads and rivers global variables.
                    if "river" in filename:
                        print("projecting and clipping line feature: ", filename)
                        lineProjected = self.projectFC(fullPath,filename.replace(".shp","")+"projected",self.fulloutputGDB,self.outputSR,self.outputDatum)
                        self.riverFC = arcpy.analysis.Clip(lineProjected,self.studyAreaSet,str(self.lineFD) + "\\" + "rivers")

                        arcpy.CheckOutExtension("Spatial")
                        arcpy.env.workspace = self.fulloutputGDB
                        print(self.studyAreaSet)
                        arcpy.env.extent = "StudyArea"
                        #create river buffers. Will need to add parameter to set extent to study area.
                        self.Riverbuffer =EucDistance(self.riverFC,cell_size="25")
                        self.riversClassified = Reclassify(self.Riverbuffer,"VALUE",RemapRange(self.riverRemap))
                        self.riversClassified.save(self.fulloutputGDB + "\\rivers_classified")

                        #test to see if deleting the river buffer will give an error eventually
                        arcpy.Delete_management(self.Riverbuffer)
                        #end

                        arcpy.Delete_management(lineProjected)



                    elif "roads" in filename:
                        print("projecting and clipping line feature: ", filename)
                        lineProjected = self.projectFC(fullPath,filename.replace(".shp","")+"projected",self.fulloutputGDB,self.outputSR,self.outputDatum)
                        self.roadsFC = arcpy.analysis.Clip(lineProjected,self.studyAreaSet,str(self.lineFD) + "\\" + "roads")

                        arcpy.CheckOutExtension("Spatial")
                        print(self.studyAreaSet)
                        arcpy.env.workspace = self.fulloutputGDB
                        arcpy.env.extent = "StudyArea"
                        #create road buffers. Will need to add parameter to set extent to study area.
                        self.roadBuffer =EucDistance(self.roadsFC,cell_size="25")
                        self.roadsClassified = Reclassify(self.roadBuffer,"VALUE",RemapRange(self.roadRemap))
                        self.roadsClassified.save("roads_classified")

                        #test to see if deleting this will give an error
                        arcpy.Delete_management(self.roadBuffer)
                        #end

                        arcpy.Delete_management(lineProjected)
                    else:
                        continue

                elif ".gdb" in filename or ".gdb" in dirpath or ".gdb" in dirnames:
                    print("skipping the output gdb")
        self.checkSuccessStatus()

    #retrieves and organizes polygon features
    def importPolygonFeatures(self,workspace):
        PolyFeatureClasses = []
        #setup a walk variable with arcpy walk to loop through subfolders
        walk = arcpy.da.Walk(workspace, datatype="FeatureClass", type="Polygon")
        #for each file in subfolder in main directory
        for dirpath, dirnames, filenames in walk:
            #look at subfolder path
            print("looking into the directory path: ", dirpath)
            #for each file in subfolder
            for filename in filenames:
                if ".gdb" not in filename and ".gdb" not in dirpath and ".gdb" not in dirnames:
                    print("looking into filename: ",filename)
                    #if park feature class or landcover feature class is accessed skip it.
                    if "park" in str(filename):
                        print("found the park feature class")

                    #if NTS50 polygon is found, clip it. Store the NTS50 value in a global variable
                    elif "NTS50" in filename:
                        polyProjected = self.projectFC(os.path.join(dirpath, filename),filename.replace(".shp","")+"_projected",self.fulloutputGDB,self.outputSR,self.outputDatum)
                        self.NTS50 = arcpy.analysis.Clip(polyProjected,self.studyAreaSet,str(self.polygonFD) + "\\" + filename.replace(".shp","")+"_clipped")
                        arcpy.Delete_management(polyProjected)
                    PolyFeatureClasses.append(filename)
                elif ".gdb" in filename and ".gdb" in dirpath and ".gdb" in dirnames:
                    continue
        self.checkSuccessStatus()


    #projects rasters
    def projectRaster_Custom(self,RasterInput,Raster_output,outputWorkspace,outCoordSystem,outDatum):

        desc = arcpy.Describe(RasterInput)
        spatialRef = desc.spatialReference
        print("check coordinate system of raster ",RasterInput)
        #if feature coord system is unknown, shut program down and alert user.
        #If feature coordinate system is known check if it matches. If not, project it.
        if spatialRef.name  == "Unknown":
            print("error! Coordinate system of FC {},is unknown".format(RasterInput), " please give it a coord system and try again")
            exit()

        elif spatialRef.name != "Unknown" and spatialRef.name != outDatum:
            print("changing datum to: {}".format(outDatum))
            return arcpy.management.ProjectRaster(RasterInput,str(outputWorkspace) + "\\{}".format(Raster_output),arcpy.SpatialReference(self.outputSR),cell_size="25")

        elif(spatialRef.name  != outCoordSystem and spatialRef.name  == outDatum):
            print("The raster coordinate system has the correct datum, but is not projected yet. Projecting into the {} planar coordinate system".format(outCoordSystem))
            return arcpy.management.ProjectRaster(RasterInput,str(outputWorkspace) + "\\{}".format(Raster_output),arcpy.SpatialReference(self.outputSR),cell_size="25")

        elif spatialRef.name  == outCoordSystem:
            print("doing import with no projecting needed")

        else:
            print("the datum is incorrect, please check the fc")
        self.checkSuccessStatus()

    #organizes and reclassifies all raster data
    def importRasterFeatures(self,workspace):
        RasterData = []
        walk = arcpy.da.Walk(workspace,datatype = "RasterDataset")

        DEM_rasters = []

        for dirpath, dirnames, filenames in walk:
            print("looking into the directory path: ", dirpath)

            for filename in filenames:
                if ".gdb" not in filename and ".gdb" not in dirpath and ".gdb" not in dirnames:
                    print("looking at file: ",filename)
                    fullPath =os.path.join(dirpath, filename)
                    print("found in folder location: ",dirpath)
                    desc = arcpy.Describe(fullPath)
                    RasterData.append(fullPath)
                    print("Data Type: " + desc.dataType)
                    if "dem" in filename:
                        print("storing DEM raster")
                        print("found the DEM",filename)
                        DEM_rasters.append(fullPath)

                    if "landcov" in filename:
                        print("found the landcover raster")
                        self.LandcoverR = self.projectRaster_Custom(fullPath,"Landcover_classes",self.fulloutputGDB,self.outputSR,self.outputDatum)

                        arcpy.CheckOutExtension("Spatial")
                        arcpy.env.workspace = self.fulloutputGDB
                        arcpy.env.extent = "StudyArea"
                        self.landcoverClassified =  Reclassify(self.LandcoverR,"VALUE",RemapValue(self.Landcoverremap))
                        self.landcoverClassified.save("landcover_ranked")
                if ".gdb" in filename and ".gdb" in dirpath and ".gdb" in dirnames:
                    print("this is the output gdb, skipping")

        print("dem rasters found: ", DEM_rasters)

        DEM_unproj = arcpy.management.Mosaic(DEM_rasters,DEM_rasters[0])

        self.DEM = self.projectRaster_Custom(DEM_unproj,"DEM_merged",self.fulloutputGDB,self.outputSR,self.outputDatum)

        arcpy.CheckOutExtension("Spatial")
        arcpy.env.workspace = self.fulloutputGDB
        arcpy.env.extent = "StudyArea"

        self.slopeDEM = Slope(self.DEM,"DEGREE")
        self.slopeDEM.save("slope_DEM")
        self.slopeClassified = Reclassify(self.slopeDEM,"VALUE",RemapRange(self.slopeRemap))
        self.slopeClassified.save("slope_ranked")

        print("list of rasters found: ", RasterData)

        self.checkSuccessStatus()

    #creates total cost surface.
    def createWeightedOverlay(self):
        arcpy.CheckOutExtension("Spatial")
        arcpy.CheckOutExtension("intelligence")
        env.workspace = self.fulloutputGDB

        remapScheme = RemapValue([[1,1],[2,2],[3,3]])

        inRaster1 =  self.roadsClassified.name
        inRaster2 =  self.riversClassified.name
        inRaster3 =  self.landcoverClassified.name
        inRaster4 =  self.slopeClassified.name

        myWOTable = WOTable([[inRaster1, 15, "VALUE", remapScheme],
                     [inRaster2, 40, "VALUE", remapScheme],
                     [inRaster3, 30, "VALUE", remapScheme],
                     [inRaster4, 15, "VALUE", remapScheme]
					          ], [1, 3, 1])

        # create total cost surface.
        outWeightedOverlay = WeightedOverlay(myWOTable)

        outWeightedOverlay.save("fcostsurface")

        self.totalCostSurface = outWeightedOverlay

        print("total cost surface path is: ",self.totalCostSurface)
        print("start point vector", self.StartPoint)
        print("end point vector: ",self.endPoint)

        arcpy.ValidateTableName(self.pipelineVector)
        self.pipelineVector = arcpy.intelligence.LeastCostPath(self.totalCostSurface,self.StartPoint,self.endPoint,"pipelinevector")
        with arcpy.da.SearchCursor(self.pipelineVector,"SHAPE@LENGTH") as findLength:
            for row in findLength:
                print("the length of the pipline is: {} meters".format(row[0]))

        self.checkSuccessStatus()


    def populateFinalMap(self,aprxpath,finalaprxFolder):
        arcpy.env.workspace = self.fulloutputGDB

        #summon template aprx.
        print("looking at aprx path of: ",aprxpath)
        aprx = MAP.ArcGISProject(aprxpath)

        #save a copy of template aprx
        aprx.saveACopy(str(aprxpath).replace(".aprx","")+"_BK.aprx")
        print("backup aprx path is: ",str(aprxpath).replace(".aprx","")+"_BK.aprx")

        #lists maps in the template aprx
        arcpy.env.overwriteOutput = True
        maps = aprx.listMaps()
        for Map in maps:
            print(Map.name)
            print(Map.mapType)
            print(Map.mapUnits)
            print(Map.spatialReference.name)

        #store pipeline map
        pipeline_map = aprx.listMaps("Pipeline Route")[0]

        #list feature classes to be added from CypressHills.gdb to the project template aprx pipeline map.
        fcList = ["start","end","pipelinevector","rivers","roads","StudyArea"]

        #for each feature class to be added to pipeline map
        for fc in fcList:
            print("now attaching to pipeline map a file path of: {} to the pipeline map".format(fc))

            #create layer file from each feature class
            layer = arcpy.management.MakeFeatureLayer(fc)
            fcName = os.path.basename(str(fc))

            #save each layer file to the data path
            finalPath = os.path.join(finalaprxFolder,fcName+".lyrx")
            print(finalPath)
            lyrFile = arcpy.management.SaveToLayerFile(layer,finalPath)



            #add layer to pipeline map
            lyrFile = MAP.LayerFile(lyrFile)
            pipeline_map.addLayer(lyrFile)

            #summon the Final Project Template layout
            layout = aprx.listLayouts("GEOS456_FinalProject_Template")[0]

            #summon legend element
            legend = layout.listElements("LEGEND_ELEMENT", "Legend")[0]

            #change position y and x of legend
            legend.elementPositionX = 14.4774
            legend.elementPositionY = 5.4916
            legend.elementHeight = 0.7236
            legend.elementWidth = 1.8938

            self.checkSuccessStatus()
        renameDict = {"start_Layer":"start point","end_Layer":"end point","pipelinevector_Layer":"proposed pipeline","rivers_Layer":"rivers","roads_Layer":"roads","StudyArea_Layer":"study area"}

        #rename map layers to something readable based on dictionary values.
        for lyr in pipeline_map.listLayers():
            print("current name of layer is: {}".format(lyr.name))
            layerName = str(lyr.name)
            lyr.name = lyr.name.replace(layerName,renameDict[layerName])
            print("new layer name is: {}".format(lyr.name))

        #save results to a new backup aprx called FinalAprx.aprx
        aprx.saveACopy("{}\FinalAprx.aprx".format(finalaprxFolder))

        #print results in a pdf called GEOS456_FP_Pan_Justin1
        layout.exportToPDF(r"{}\GEOS456_FP_Pan_Justin1.pdf".format(finalaprxFolder))

    def printStatistics(self):
        #checkout the spatial extension
        arcpy.CheckOutExtension("Spatial")

        #set workspace to cypress gdb
        arcpy.env.workspace = self.fulloutputGDB

        #create zonal statistics tables for the mean elevation and slope.
        ElevAvg = ZonalStatisticsAsTable(self.studyArea,"NAME",self.DEM,"mean_elev_park")
        SlopeAvg  = ZonalStatisticsAsTable(self.studyArea,"NAME",self.slopeDEM,"mean_slope_park")

        #set a list of the tables, with their corresponding subject and units
        Tables = [ElevAvg,SlopeAvg]
        subject = ["elevation","slope"]
        units = ["meters","degrees"]

        #loop parallel through the Tables, subject, and units lists
        for tbl,subjects,unit in zip(Tables,subject,units):
            #for each item in the lists, print the mean found for each subject.
            #e.g. print elevation mean from elevation table, and then print slope mean from slope table.
            with arcpy.da.SearchCursor(tbl,["MEAN"]) as statCursor:
                for row in statCursor:
                    print("the mean {} is {} {}s".format(subjects,row[0],unit))

        #print the NTS50 grids which were found within the park area.
        with arcpy.da.SearchCursor(self.NTS50,"NAME") as NTSareaCursor:
            for row in NTSareaCursor:
                print("the NTS area: {} was found in the park area".format(row[0]))

        self.checkSuccessStatus()

    #function prints the area found for each landcover type.
    def calculateLandcoverTypes(self):
        arcpy.management.AddField(self.LandcoverR,"Area_sqm","FLOAT")
        arcpy.management.CalculateField(self.LandcoverR,"Area_sqm","!COUNT!*25*25")
        with arcpy.da.SearchCursor(self.LandcoverR,["VALUE","Area_sqm"]) as printLandcoverAreas:
            for row in printLandcoverAreas:
                print("area of landcover class {} is {} square meters".format(row[0],row[1]))

        self.checkSuccessStatus()
    #function deletes all remaining intermediate data.
    def deleteAllIntermediateData(self):
        arcpy.env.workspace = self.fulloutputGDB
        Intermediatedata = ["EucDist_rive1","EucDist_road1","fcostsurface","landcover_ranked","rivers_classified","roads_classified","slope_ranked"]
        for interdata in Intermediatedata:
            arcpy.Delete_management(interdata)
        self.checkSuccessStatus()


def main():
    #C drive paths to use for parameters.
    outputFolderPath = r"C:\GEOS456\FinalProject"
    outputGDBName = "CypressHills"
    wellsFC = r"C:\GEOS456\FinalProject\Oil_Gas\wells.shp"
    FacilitiesFC = r"C:\GEOS456\FinalProject\Oil_Gas\facilities.shp"
    studyArea = r"C:\GEOS456\FinalProject\Base_72E09\rec_park.shp"
    finalProjData = r"C:\GEOS456\FinalProject"

    final_aprx = r"C:\GEOS456\FinalProject\GEOS456_FinalProject_Template.aprx"


    #start timer

    start = time.time()
    print("starting script")
    #create and instance of the final project class
    finalProject = FinalProjectClass(outputGDBName,outputFolderPath,FacilitiesFC,wellsFC,studyArea)


    #set the output gdb and delete previous gdb copy
    finalProject.setoutputGDB()

    #create the vector feature datasets
    finalProject.setFDs()

    #import the study area aka park area.
    finalProject.setStudyArea()

    #import and clip the point features
    finalProject.importPointFeatures()

    #import and clip the polygon features
    finalProject.importPolygonFeatures(finalProjData)

    #import and clip the line features
    finalProject.importLineFeatures(finalProjData)

    #import and reclassify the rasters
    finalProject.importRasterFeatures(finalProjData)

    #output statistics for landcover class areas and other needed statistics.
    finalProject.calculateLandcoverTypes()
    finalProject.printStatistics()

    #create the total cost surface and pipeline
    finalProject.createWeightedOverlay()

    #populate final map based on a aprx and aprx folder path
    finalProject.populateFinalMap(final_aprx,finalProjData)

    #delete all data marked as intermediate.
    finalProject.deleteAllIntermediateData()

    #mark the amount of time taken for using the script.
    end = time.time()
    print("the script ran for a total of: ",(end-start) * 10 **3,"ms or", ((end-start) * 10 **3)/60000," minutes")



if __name__ == "__main__":
    main()
