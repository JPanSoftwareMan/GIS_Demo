import arcpy

def ScriptTool(roadFeature, outputFC,bufferDist,featurestoIntersect):
    # Script execution code goes here
    bufferFC = arcpy.analysis.Buffer(roadFeature,"inclusionZone",bufferDist)
    arcpy.analysis.Intersect([bufferFC,featurestoIntersect],outputFC)

    arcpy.management.AddField(outputFC,"Hectares","FLOAT")
    arcpy.management.AddField(outputFC,"Acres","FLOAT")
    arcpy.management.CalculateField(outputFC,"Acres","!shape.area!*0.000247105")
    arcpy.management.CalculateField(outputFC,"Hectares","!shape.area!*0.0001")
    return outputFC

# This is used to execute code if the file was run but not imported
if __name__ == '__main__':

    # Tool parameter accessed with GetParameter or GetParameterAsText
    roadFeature = arcpy.GetParameterAsText(0)
    outputFC = arcpy.GetParameterAsText(1)
    bufferDist = arcpy.GetParameterAsText(2)
    featurestoIntersect = arcpy.GetParameterAsText(3)

    ScriptTool(roadFeature, outputFC,bufferDist,featurestoIntersect)

    # Update derived parameter values using arcpy.SetParameter() or