#-------------------------------------------------------------------------------
# Name:        Assignment 2 V5
# Purpose:     Runs the analysis for assignment 2
#
# Author:      845942, Justin Pan
#
# Created:     02/02/2023
# Copyright:   (c) Southern Alberta Institute of Technology Programming Department
# Licence:     Use of this code means acknowledging that Justin Pan *insert swear word* made it. You may NOT reproduce this code for commercial purposes.
#-------------------------------------------------------------------------------
import arcpy
import os

#--------------------------------------------functions to use in workflow -------------------------------------------------------------
#shows information of all shp files inside all data folders.
def describeFolder_FCs(folders):
    for folder in folders:
        arcpy.env.workspace = folder
        folderName = os.path.basename(str(folder))
        FClist = arcpy.ListFeatureClasses()
        print("--------------------")
        print("inspecting the files in the " + folderName + " folder")
        for fc in FClist:
            print("--------------------------------")
            fcDESC = arcpy.Describe(fc)
            print("inspecting file " + fcDESC.name)
            print("Data type:" + fcDESC.dataType)
            print("Geometry:" + fcDESC.shapeType)
            print("Spatial reference:" + fcDESC.spatialReference.name)
            checkSuccessStatus()
            print("------------------------------")

def fixUnknownCoordSystems(FC,properSR):
    FC_desc = arcpy.Describe(FC)
    if (str(fcDESC.spatialReference.name) == "" or str(fcDESC.spatialReference.name) =="UNKNOWN"):
        print("this feature class has an unknown coordinate system. Projecting to specified coordinate system")
        arcpy.management.DefineProjection(FC,properSR)

def standardizeDatum_FCs(FD):
    for FC in FD:
        print("standardizing datum from....")

#lists the spatial reference, data type, and geometry of the final output by accessing the output gdb.
def describeFD_FCs(GDB,sr):
    arcpy.env.workspace = GDB
    datasets = arcpy.ListDatasets(feature_type = "feature")
    datasets = [''] + datasets if datasets is not None else[]

    for dataset in datasets:
        for fc in arcpy.ListFeatureClasses(feature_dataset=dataset):
            print("-------------------------------")
            path = os.path.join(arcpy.env.workspace,dataset,fc)
            print("looking into feature class at filepath " + path)
            fcDESC = arcpy.Describe(fc)
            print("file name: " + fcDESC.name)
            print("Data type:" + fcDESC.dataType)
            print("Geometry:" + fcDESC.shapeType)
            print("Spatial reference:" + fcDESC.spatialReference.name)
            checkFCCoordSystem(fc,sr.name)
            print("------------------------------")
#extra function for listing table field properties
def extracttblFields(workspace):
    tableList = arcpy.ListTables()
    print("here we want all tables in gdb")
    print("")
    for table in tableList:
        tableDESC = arcpy.Describe(table)
        for field in tableDESC.fields:
            print("field name: ", field.name,"|","Field Type",field.type)


#checks if process was successfully completed
def checkSuccessStatus():
    print("success status: ")
    print(arcpy.GetMessages())
    print("---------------------------------------------")

#creates the study area polygon and imports it to the dls feature dataset
def create_import_StudyArea(raw_TWP,raw_GPS,FD):
    print("---------------------------------------------")
    print("creating study area")
    twpLayer = arcpy.MakeFeatureLayer_management(raw_TWP,"TWP_layer")
    gpsLayer = arcpy.MakeFeatureLayer_management(raw_GPS,"GPS_layer")
    arcpy.SelectLayerByLocation_management(twpLayer,"INTERSECT",gpsLayer)
    print("importing study area to dls feature dataset")

    checkSuccessStatus()
    return arcpy.CopyFeatures_management(twpLayer, str(FD) + "\\Study_Area")


#clips all base features and imports it to the base feature dataset
def clip_import_BaseFeatures(base_folder,studyArea,base_FD):
    print("starting to clip base features")
    arcpy.env.workspace = base_folder
    FClist = arcpy.ListFeatureClasses()
    for fc in FClist:
        print("--------------------------------------------------------------------------------")
        print("clipping " + fc + " to study area and importing to base feature dataset")
        clippedFC = arcpy.analysis.Clip(fc,studyArea,str(base_FD) + "\\" + fc.replace(".shp","") + "clipped")
        arcpy.management.Dissolve(clippedFC, str(base_FD) + "\\" +fc.replace(".shp","")+ "merged")
        arcpy.Delete_management(str(base_FD) + "\\" + fc.replace(".shp","") + "clipped")
        checkSuccessStatus()
        print("--------------------------------------------------------------------------------")

#check if gdb from previous run exists, if it does, delete it, and create the gdb again.
def setoutputGDB(outputGDB_Path):
    if arcpy.Exists(outputGDB_Path):
        print("deleting previously created gdb")
        arcpy.Delete_management(outputGDB_Path)
    print("creating new output gdb")
    checkSuccessStatus()
    return arcpy.management.CreateFileGDB("C:\GEOS456\Assign02", "Assignment02.gdb")

#import gps point FC to GPS FD and rename it.
def importRename_GPS_pt(GPS_shp,GPS_FD):
    print("importing and renaming gps point feature class")
    arcpy.conversion.ExportFeatures(GPS_shp, str(GPS_FD) + "\\GPS_point")
    checkSuccessStatus()

#check if feature classes were projected properly
def checkFCCoordSystem(FC,appropriate_sr):
    fcDESC = arcpy.Describe(FC)
    if(str(fcDESC.spatialReference.name) == appropriate_sr):
        print("feature spatial reference: " + str(fcDESC.spatialReference.name))
        print("correct spatial reference: " + appropriate_sr)
        print("file is in correct coordinate system")
    else:
        print("feature spatial reference: " + str(fcDESC.spatialReference.name))
        print("correct spatial reference: " + appropriate_sr)
        print("spatial reference is not correct for FC: ",FC)
    checkSuccessStatus()

#checks the DLS description of the study area feature class
def findDLS_Description(twppath,field):
    with arcpy.da.SearchCursor(twppath,field) as findDLS:
        for row in findDLS:
            print("study area is in: " + row[0])
            checkSuccessStatus()


#--------------------------------------------main workflow -------------------------------------------------------------


#set input data folders .
GPS_folder = r"C:\GEOS456\Assign02"
Base_folder = r"C:\GEOS456\Assign02\Base"
DLS_folder = r"C:\GEOS456\Assign02\DLS"

#set the township shp and gps shp files
TWP_shp = r"C:\GEOS456\Assign02\DLS\82I_TWP.shp"
GPS_shp = r"C:\GEOS456\Assign02\GSP_Pointe.shp"

#output coord system
sr = arcpy.SpatialReference("NAD 1983 UTM Zone 11N")

outputGDB_Path = r"C:\GEOS456\Assign02\Assignment02.gdb"
#set the output gdb and delete any existing copies of it from previous runs
outputGDB = setoutputGDB(outputGDB_Path).getOutput(0)

#describe all shp file in each folder
describeFolder_FCs([GPS_folder,Base_folder,DLS_folder])

#create the feature datasets for the output gdb
Base_FD = arcpy.management.CreateFeatureDataset(outputGDB,"BASE",sr)
GPS_FD = arcpy.management.CreateFeatureDataset(outputGDB,"GPS",sr)
TWP_FD = arcpy.management.CreateFeatureDataset(outputGDB,"DLS",sr)


#create study area and import to DLS FD
Study_area = create_import_StudyArea(TWP_shp,GPS_shp,TWP_FD)

#read the dls description of the study area based on the dls description field name
findDLS_Description(Study_area, "DESCRIPTOR")

#clip base features to study area, then import into base feature dataset
clip_import_BaseFeatures(Base_folder,Study_area,Base_FD)

#rename gps point and import to GPS feature dataset.
importRename_GPS_pt(GPS_shp,GPS_FD)

#check cooordinate system of output gdb to see if results were converted correctly.
describeFD_FCs(outputGDB,sr)

