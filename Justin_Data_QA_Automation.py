#Created by: Justin Pan
#Created at: July 15, 2021
#Last Modified at: May 5, 2022
#Description:
#This script demos how to make QA automation to a point feature layer in a file geo database 
#It can find the following data issues:
#   1. If the latitudes and longitudes are out of range based on the point geometry coordinates 
#   2. If the project names are correct
#   3. If the material types are correct
#   4. If Object heights are valid

import arcpy
import os
import datetime

inputFC  = r"C:\Temp\JustinData\JustinDemoData.gdb\JustinPointFC"
if not arcpy.Exists(inputFC):
    print('The input data does not exist. Please make sure the feature class path is correct')
    exit(0)
##          0           1           2           3           4               5               6           7       8


ProjectNames = ['Nose Hill']

LatitudeMin = 51.0742031
LatitudeMax = 51.1477041
LongitudeMin = -114.1616387
LongitudeMax = -114.0406285 

MaterialTypes= ['Wood','Steel']

ObjectHeightMin = 0
ObjectHeightMax = 20
print('QA Parameters:')
print('------------')
print('Valid Project Names are:')
print(ProjectNames)
print('------------')
print('Valid Material Types are:')
print(MaterialTypes)
print('------------')
print('Latitude Min:')
print(LatitudeMin)
print('Latitude Max:')
print(LatitudeMax)
print('------------')
print('Object Height Min:')
print(ObjectHeightMin)
print('ObjectHeight Max:')
print(ObjectHeightMax)
print('------------')

#Index      0           1           2           3           4               5               6           7       8
fields = ['OID@','ProjectName','Latitude','Longitude','MaterialType','ObjectHeight', 'CreatedAt', 'SHAPE@X','SHAPE@Y']

print('The QA automation results:')

# For each row, print the WELL_ID and WELL_TYPE fields, and
# the feature's x,y coordinates
with arcpy.da.SearchCursor(inputFC, fields) as cursor:
    for row in cursor:
        #print(u'{0}, {1}, {2}'.format(row[0], row[1], row[2]))
        if row[1] not in ProjectNames:
            print ('Error: for OID = ' + str(row[0]) + ', Project Name ' + row[1] + ' is not in the available list of (' +  ' '.join([str(item + ',') for item in ProjectNames]) + ")"   )    
        if row[4] not in MaterialTypes:
            print ('Error: for OID = ' + str(row[0]) + ', Material Type ' + row[4] + ' is not in the available list of (' +  ' '.join([str(item + ',') for item in MaterialTypes]) + ")"   )    

        if row[2] < LatitudeMin:
            print ('Error: for OID = ' + str(row[0]) + ', Latitude < Latitude Min (' + str(row[2]) + ' < ' +  str(LatitudeMin) + ")"   )
        if row[2] > LatitudeMax:
            print ('Error: for OID = ' + str(row[0]) + ', Latitude > Latitude Max (' + str(row[2]) + ' > ' +  str(LatitudeMax) + ")"  )
        if row[3] < LongitudeMin:
            print ('Error: for OID = ' + str(row[0]) + ', Longitude < Longitude Min (' + str(row[3]) + ' < ' +  str(LongitudeMin) + ")"  )
        if row[3] > LongitudeMax:
            print ('Error: for OID = ' + str(row[0]) + ', Longitude > Longitude Max (' + str(row[3]) + ' > ' +  str(LongitudeMax) + ")"  )
        if row[5] < ObjectHeightMin:
            print ('Error: for OID = ' + str(row[0]) + ', ObjectHeight < ObjectHeight Min (' + str(row[5]) + ' < ' +  str(ObjectHeightMin) + ")"  )
        if row[5] > ObjectHeightMax:
            print ('Error: for OID = ' + str(row[0]) + ', ObjectHeight > ObjectHeight Max (' + str(row[5]) + ' > ' +  str(ObjectHeightMax) + ")"  )
        

del cursor

print('The data QA automation has been finished successfully')




    