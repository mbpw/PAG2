import arcpy

infc = arcpy.GetParameterAsText(0)

# Enter for loop for each feature
#
for row in arcpy.da.SearchCursor(infc, ["OID@", "SHAPE@"]):
    # Print the current line ID

    print("Feature {0}:".format(row[0]))

    #Set start point
    startpt = row[1].firstPoint

    #Set Start coordinates
    startx = startpt.X
    starty = startpt.Y

    #Set end point
    endpt = row[1].lastPoint

    #Set End coordinates
    endx = endpt.X
    endy = endpt.Y
