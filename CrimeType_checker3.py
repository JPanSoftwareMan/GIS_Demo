#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:     This script checks violent crime statistics for Arlington County, Virginia
# User:        000845942
# Author:      Justin Pan
#
# Created:     01/26/2023
# Copyright:   (c) 845942 2023
#-------------------------------------------------------------------------------
import arcpy

class Crimecheck:
    #intialize parameters for the crime checking function
    def __init__(self, dataPath, outputGDB, crimefcs, precintfc, landmarkfc):
        self.dataPath = dataPath
        self.outputGDB = outputGDB
        self.crimefcs = crimefcs
        self.precintfc = precintfc
        self.landmarkfc = landmarkfc

    #function finds which landmark with most crime for each crime type.
    def findCrimeMax(self,landmarkOutput, crimeCountField,landmarkName,crime):
        print("---------------------------------------------------------------------")
        print("finding landmark with the most " + crime.split(".")[0] + " within 250 meters of the landmark...........")
        queryCrime = "ORDER BY " + str(crimeCountField) + " DESC"
        with arcpy.da.SearchCursor(landmarkOutput, [crimeCountField,landmarkName],sql_clause=(None, queryCrime)) as findMax:
            for row in findMax:
                print(str(row[1]) + " has the most " + crime.split(".")[0] + " at " + str(row[0]) + " incidents")
                break
        print("----------------------------------------------------------------------")
    #function shows feature class row results.
    def printFCtable(self,FC):
        print("printing table results")

        with arcpy.da.SearchCursor(FC, "*") as printTable:
            for row in printTable:
                print(row)
    #function creates feature classes with crime amount per precinct
    def findCrimeperPrecinct(self,crime, precinctOutput):
        #create feature class with amount of crime type in each precinct
        print("---------------------------------------------------------------------")
        print("finding amount of " + crime.split(".")[0] + " in each precinct.....")
        arcpy.analysis.SpatialJoin(self.precintfc, crime, precinctOutput)
        self.printFCtable(precinctOutput)
        print("---------------------------------------------------------------------")

    #function creates feature classes with crime amoutn within 250 meters of a landmark
    def crimes_within_250m_landmark(self,crime,landmarkOutput):
        print("---------------------------------------------------------------------")
        print("finding " + crime.split(".")[0] + " within 250 meters of a landmark......")
        arcpy.analysis.SpatialJoin(self.landmarkfc,crime,landmarkOutput,join_type = "KEEP_COMMON", match_option = "WITHIN_A_DISTANCE", search_radius = 250)
        self.printFCtable(landmarkOutput)
        print("---------------------------------------------------------------------")

    def rename_field_in_multiFC(self,fcList,oldFieldName,newFieldName):
        for fc in fcList:
            arcpy.management.AlterField(fc, oldFieldName, newFieldName,newFieldName)



    #function outputs feature classes to store information on crimes within 250 meters of a landmark and crime count per precinct.
    def CheckCrimes(self):
        arcpy.env.overwriteOutput = True
        arcpy.env.workspace = self.dataPath

        #create output gdb in data path
        outputGDB = arcpy.management.CreateFileGDB(arcpy.env.workspace,self.outputGDB)

        #for each crime type feature class
        for crime in self.crimefcs:

            #create output gdb file paths for crime output feature classes
            crimeOutput = str(outputGDB) + "\\" + crime.split(".")[0] + "per_Precinct"
            landmarkOutput = str(outputGDB) + "\\" + crime.split(".")[0] + "within_250m_Landmark"

            #find crimes per precinct
            self.findCrimeperPrecinct(crime, crimeOutput)

            #find crimes within 250 meters of a landmark.
            self.crimes_within_250m_landmark(crime,landmarkOutput)


            FC_outputs = [crimeOutput,landmarkOutput]
            newFieldName = "Amount_of_" + crime.split(".")[0]
            oldFieldName = "Join_Count"

            #rename join field of each crime type feature class to amount of x crime
            self.rename_field_in_multiFC(FC_outputs,oldFieldName,newFieldName)


            #set landmark feature class field and field value of join count
            landmarkName = "LANDNAME"


            #find the landmark which has had the most incidents of the crime type
            self.findCrimeMax(landmarkOutput,newFieldName,landmarkName,crime)

def main():

    #set workspace
    dataPath = r"C:\GEOS456\Assign01"

    outputGDB = "crimesData"

    #create a list of violent crime feature classes, and set the precinct and landmark feature classes
    crimefcs = ["Arsons.shp", "burglaries.shp", "Assault.shp"]
    precintfc = "Precincts.shp"
    landmarkfc = "Landmarks.shp"

    #run the check crimes function to complete all tasks.
    #parameters: path where all data input will is stored, name of output gdb, the input crime feature classes, the input precinct feature class, the input landmark feature class
    PrC = Crimecheck(dataPath, outputGDB, crimefcs, precintfc, landmarkfc)

    PrC.CheckCrimes()

if __name__ == '__main__':
    main()
