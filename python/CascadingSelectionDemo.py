# Description: This Cascading selection tool is used as a demo on how to make a cascading style selection to get the data bassed on 3 fileds / attributes: SPECIES, YEAR 
# and BUFF_DIST from feature class C:\TEMP\Birds.gdb\Colonial_Nesting_Birds. The query result can be exported to formts of Excel/CSV, shape files, feature class in FGDB, 
# Map PDF and Google KMZ.
# Author: Justin Pan
# Email: genjustinshooter@gmail.com
# Designed and developed at: Jan 1, 2021    

import arcpy
from arcpy import env
import sys, traceback
import os
import csv
import xlwt 
from xlwt import Workbook 
import time
from datetime import datetime
import pandas as pd
  
class CascadingSelection:
        #initialize application
        def __init__(self, DataFeatureClass, SelectionSpeciesValue, SelectionYearValue, SelectionBuffDistValue,FileOutputType,OutputFolder,StrTimeStamp,MapTemplate):
                #initialize MS Access Manager object to work with MS Access DB
                self.dataFeatureClass = DataFeatureClass
                self.selectionSpeciesValue = SelectionSpeciesValue
                self.selectionYearValue = SelectionYearValue
                self.selectionBuffDistValue = SelectionBuffDistValue
                self.fileOutputType = FileOutputType
                self.outputFolder = OutputFolder
                self.strTimeStamp = StrTimeStamp
                self.mapTemplate = MapTemplate
                self.express1 = " SPECIES = '" + self.selectionSpeciesValue + "' and YEAR = '" + self.selectionYearValue + "' and BUFF_DIST = " + self.selectionBuffDistValue   
                self.temLayer = "layerTemp_" + self.strTimeStamp  #self.outputFolder + os.sep + 
                arcpy.AddMessage("The query expression is: " + self.express1)

        def exportToFCInFGDB(self):
                arcpy.AddMessage("Exporting to Feature class in FGDB ...")
                arcpy.CreateFileGDB_management(self.outputFolder, "CascadingSelecctionFGDB_" + self.strTimeStamp + ".gdb")
                outputFGDB = self.outputFolder + os.sep + "CascadingSelecctionFGDB_" + self.strTimeStamp + ".gdb"
                tempLayer = self.temLayer
                arcpy.MakeFeatureLayer_management(self.dataFeatureClass, tempLayer,self.express1)
                # Write the selected features to a new featureclass
                arcpy.CopyFeatures_management(tempLayer, outputFGDB + os.sep + "SelectedResult_" + self.strTimeStamp)
                arcpy.AddMessage("--------------------------------------")
                arcpy.AddMessage("The output feature class is: " + outputFGDB + os.sep + "SelectedResult_" + self.strTimeStamp )

        def exportToShapeFile(self):
                tempFGDBForShape = "tempFGDBForShape_" + self.strTimeStamp + ".gdb"
                if not arcpy.Exists(tempFGDBForShape):
                        arcpy.CreateFileGDB_management(self.outputFolder, tempFGDBForShape)
                outputFGDB = self.outputFolder + os.sep + tempFGDBForShape
                tempLayer = self.temLayer + "Shape"
                arcpy.MakeFeatureLayer_management(self.dataFeatureClass, tempLayer,self.express1)
                # Write the selected features to a new featureclass
                arcpy.CopyFeatures_management(tempLayer, outputFGDB + os.sep + "SelectedResult_" + self.strTimeStamp)

                arcpy.FeatureClassToShapefile_conversion(outputFGDB + os.sep + "SelectedResult_" + self.strTimeStamp, self.outputFolder)
                arcpy.AddMessage("The output shape file is: " + self.outputFolder + os.sep + "SelectedResult_X" + self.strTimeStamp + ".shp")
                arcpy.Delete_management(outputFGDB)

        def exportToKMZ(self):
                arcpy.AddMessage("Exporting to Google KMZ ...")
                arcpy.env.overwriteOutput = True
                mxd = arcpy.mapping.MapDocument(self.mapTemplate)
                try:
                        lyr = arcpy.mapping.ListLayers(mxd)[0]
                        lyr.definitionQuery = self.express1
                        #arcpy.SelectLayerByAttribute_management (lyr, "NEW_SELECTION", "OBJECTID < 0 ")
                        #outputKMZ = self.outputFolder + os.sep + "CascadingSelection_" + self.strTimeStamp + ".kmz"
                        arcpy.SelectLayerByAttribute_management(lyr, "CLEAR_SELECTION")
                        outputKMZ = self.outputFolder + os.sep + "CascadingSelection_" + self.strTimeStamp + ".kmz"
                        mxd.save()
                        arcpy.LayerToKML_conversion(lyr,outputKMZ,None,'false','DEFAULT','1024','96')
                        arcpy.AddMessage("The output KMZ file is: " + outputKMZ)
                except arcpy.ExecuteError:
                        arcpy.AddMessage("Error on exportToKMZ: " + arcpy.GetMessages())
                
        def exportToPDFMap(self):
                arcpy.env.overwriteOutput = True
                mxd = arcpy.mapping.MapDocument(self.mapTemplate)
                try:
                        lyr = arcpy.mapping.ListLayers(mxd)[0]
                        lyr.definitionQuery = " OBJECTID > 0 "
                        arcpy.SelectLayerByAttribute_management (lyr, "NEW_SELECTION", self.express1)
                        mxd.save()
                        #outputKMZ = self.outputFolder + os.sep + "CascadingSelection_" + self.strTimeStamp + ".kmz"
                        outputMap = self.outputFolder + os.sep + "CascadingSelectionMap_" + self.strTimeStamp + ".PDF"
                        arcpy.mapping.ExportToPDF(mxd, outputMap)

                except arcpy.ExecuteError:
                        arcpy.AddMessage("Error on exportToPDFMap: " + arcpy.GetMessages())

        def exportToFileExcelandCSV(self):
                in_delimiter = "COMMA"
                # Workbook is created 
                workBook = Workbook() 
                # The add_sheet is used to create sheet. 
                sheet1 = workBook.add_sheet('Sheet 1') 
                fields = arcpy.ListFields(self.dataFeatureClass)
                
                intColumn = 0
                for field in fields:
                        sheet1.write(0,intColumn,field.name)
                        intColumn += 1
                intFieldsLength = len(fields)
                arcpy.AddMessage("fields length is: " + str(intFieldsLength) )
                fields1 = ["*"]
                intRow = 1
                #express1 = " SPECIES = '" + self.selectionSpeciesValue + "' and YEAR = '" + self.selectionYearValue + "' and BUFF_DIST = " + self.selectionBuffDistValue   
                arcpy.AddMessage("Query is: " + self.express1)
                with arcpy.da.SearchCursor(self.dataFeatureClass, fields1, self.express1) as cursor:
                        for row in cursor:
                                intColumn = 0
                                while intColumn < intFieldsLength:
                                        sheet1.write(intRow, intColumn,  str(row[intColumn]) )
                                        intColumn += 1
                                intRow +=1
                strOutputFilePath = self.outputFolder + os.sep +   'CascadingSelection_'   +  self.strTimeStamp + '.xls'
                strOutputFilePathCSV = self.outputFolder + os.sep +   'CascadingSelection_'   +  self.strTimeStamp + '.csv'
                
                arcpy.AddMessage("The output Excel file is: " + strOutputFilePath)
                workBook.save( strOutputFilePath) 
                dataFile = pd.read_excel (strOutputFilePath)
                dataFile.to_csv (strOutputFilePathCSV, index = None, header=True)


def main():
        now = datetime.now()
        str_date_time = now.strftime("%Y_%m_%d_%H_%M_%S")
        arcpy.AddMessage('The processing began at: ' + str_date_time)

        strTimeStamp =str( time.time()).replace(".","")
        arcpy.AddMessage("The date time stamp = " + strTimeStamp)

        dataFeatureClass =  arcpy.GetParameterAsText(0)
        selectionSpeciesValue =  arcpy.GetParameterAsText(1)
        selectionYearValue =  arcpy.GetParameterAsText(2)
        selectionBuffDistValue =  arcpy.GetParameterAsText(3)
        fileOutputType =  arcpy.GetParameterAsText(4)
        OutputFolder =  arcpy.GetParameterAsText(5)
        mapTemplate =  arcpy.GetParameterAsText(6)
        # For debugging only:         
        # arcpy.AddMessage(dataFeatureClass)
        # arcpy.AddMessage(selectionSpeciesValue)
        # arcpy.AddMessage(selectionYearValue)
        # arcpy.AddMessage(selectionBuffDistValue)
        # arcpy.AddMessage(fileOutputType)
        # arcpy.AddMessage(OutputFolder)
        cascadingSelection = CascadingSelection(dataFeatureClass, selectionSpeciesValue,selectionYearValue, selectionBuffDistValue,fileOutputType,OutputFolder,strTimeStamp, mapTemplate )
        if fileOutputType.upper() == "CSV AND EXCEL":
                cascadingSelection.exportToFileExcelandCSV()
        if fileOutputType.upper() == "Feature Class in FGDB".upper():
                cascadingSelection.exportToFCInFGDB()
        if fileOutputType.upper() == "SHAPE FILE":
                cascadingSelection.exportToShapeFile()
        if fileOutputType.upper() == "Google KMZ".upper():
                cascadingSelection.exportToKMZ()
        if fileOutputType.upper() == "MAP PDF":
                cascadingSelection.exportToPDFMap()
        
        now = datetime.now()
        str_date_time = now.strftime("%Y_%m_%d_%H_%M_%S")
        arcpy.AddMessage('The processing ended at: ' + str_date_time)

if __name__ == '__main__':
    main()




