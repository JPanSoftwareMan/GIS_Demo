#Created by: Justin Pan
#Created at: July 10, 2021
#Last Modified at: May 2, 2022
#Description: 
#This script can create a File Geo database and a point feature class with WGS84 spatial reference. 
#It also adds some attributes and insert 6 sample points.


import arcpy
import os
import datetime

out_folder_path  = r"C:\Temp\JustinData"
out_name = r"JustinDemoData"
out_name_full = out_folder_path + os.sep + out_name + '.gdb'
out_feature_name = ''
if not arcpy.Exists(out_name_full):
    arcpy.management.CreateFileGDB(out_folder_path, out_name)
# Geographic Coordinate system "WGS 1984" (factory code=4326)
srid = arcpy.SpatialReference(4326)
JustinPointFC = "JustinPointFC"
if not arcpy.Exists(out_name_full + os.sep + JustinPointFC):
    fc = arcpy.CreateFeatureclass_management(out_name_full, JustinPointFC, "POINT", '', '', '', srid)
    outputFC = out_name_full + os.sep +  JustinPointFC
    arcpy.AddField_management(outputFC, "ProjectName", "TEXT", None, None, 100)
    arcpy.AddField_management(outputFC, "Latitude", "DOUBLE", 19, 8, None, None, "NULLABLE", "NON_REQUIRED")
    arcpy.AddField_management(outputFC, "Longitude", "DOUBLE", 19, 8, None, None, "NULLABLE", "NON_REQUIRED")
    arcpy.AddField_management(outputFC, "MaterialType", "TEXT", None, None, 20)
    arcpy.AddField_management(outputFC, "ObjectHeight", "DOUBLE", 19, 4, None, None, "NULLABLE", "NON_REQUIRED")
    arcpy.AddField_management(outputFC, "CreatedAt", "DATE", None, None, None, None, "NULLABLE", "NON_REQUIRED")

outputFC = out_name_full + os.sep +  JustinPointFC
if arcpy.Exists(outputFC):
    cursor = arcpy.da.InsertCursor(outputFC,['ProjectName','Latitude','Longitude','MaterialType','ObjectHeight', 'CreatedAt', 'SHAPE@XY'])
    createdAt = datetime.datetime.now()
    row_values = [  ('Nose Hill', '51.125919','-114.131807','Wood','1.2', createdAt, (-114.131807,51.125919)),
                    ('Nose Hill', '51.114928','-114.128889','Steel','1.52', createdAt, (-114.128889,51.114928)),
                    ('Hamptons', '51.097575','-114.096960','Wood','1342.0', createdAt, (-114.096960,51.097575)),
                    ('Nose Hill', '51.112988','-114.086145','Paper','1.5', createdAt, (-114.086145,51.112988)),
                    ('Nose Hill', '51.215539','-121.877030','Wood','1.2', createdAt, (-121.877030,51.215539)),
                    ('Nose Hill', '64.743230','-104.836226','Steel','1.2', createdAt, (-104.836226,64.743230)),
              ]
   
    for row in row_values:
        cursor.insertRow(row)

# Delete cursor object
del cursor





print('The end')




    