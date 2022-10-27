""" River Valley Delineation using Cost Distance
By Gasper Sechu 

"""

# Import system modules
import arcpy
from arcpy import env
import datetime
import os

def costdist(riv_in, cat_in, slp_in, costpath, outp):
    
    # Start time 
    start = datetime.datetime.now()
    print("Cost dist calculation started at %s" % start)
    arcpy.AddMessage ("Cost dist calculation started at %s" % start)
    arcpy.AddMessage ("\n")
    
    # Check out spatial extention
    arcpy.CheckOutExtension("Spatial") 
    
    # Environments
    env.workspace = "in_memory"
    env.scratchWorkspace = "in_memory"
    env.overwriteOutput = True
    env.cellSize = os.path.join(outp, "con_slope")
    env.snapRaster = os.path.join(outp, "con_slope") 
    
    # Select features that intersect
    selection = arcpy.SelectLayerByLocation_management(cat_in, "INTERSECT", riv_in, None, "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management(selection, os.path.join(outp, "cat_riv"), None, None, None, None)
    del selection    
    
    # Loop through layer to create tuple of field values
    field = arcpy.Describe(os.path.join(outp, "cat_riv")).OIDFieldName
    AllValues = [] # an empty list to contain the unique values
    with arcpy.da.SearchCursor(os.path.join(outp, "cat_riv"), field) as cursor:
        for row in cursor:
            if row[0] not in AllValues:
                AllValues.append(row[0]) # if the value isn"t already in the list then add it
                
        del cursor
                
    print("There is/are %s intersecting features" % AllValues[-1]) # Prints the number of intersecting features
    arcpy.AddMessage ("There are %s intersecting features" % AllValues[-1])
    arcpy.AddMessage ("\n")            

    rows = int((arcpy.GetCount_management (os.path.join(outp, "cat_riv"))).getOutput(0))
    arcpy.SetProgressor ("step", "Working..", 0, rows, 1)
    
    # Cost distance
    oid_fieldname = arcpy.Describe(riv_in).OIDFieldName
    cellResult = arcpy.GetRasterProperties_management(slp_in, "CELLSIZEX")
    cell = cellResult.getOutput(0)
    arcpy.PolylineToRaster_conversion(riv_in, oid_fieldname, os.path.join(outp, "riv_raster"), "MAXIMUM_LENGTH", "NONE", cell)
    
    with arcpy.da.SearchCursor(os.path.join(outp, "cat_riv"), ["OID@", "SHAPE@"]) as cursor:
        for row in cursor:
            print("Calculating cost distance for OID %s at %s" % (row[0], datetime.datetime.now()))
            arcpy.AddMessage ("Calculating cost distance for OID %s at %s" % (row[0], datetime.datetime.now()))
            arcpy.Select_analysis(row[1], os.path.join(outp, "catmask"))
            env.mask = os.path.join(outp, "catmask")
            costname = "cst_" + "%s" % (row[0]) # + ".tif"
            ras1 = arcpy.Raster(os.path.join(outp, "riv_raster"))
            ras2 = arcpy.Raster(slp_in)
            cost_dist = arcpy.sa.CostDistance(ras1, ras2, None, None, None, None, None, None, None); 
            cost_dist.save(os.path.join(costpath, costname))
            cost_dist = None # https://gis.stackexchange.com/questions/46897/saving-rasters-in-a-python-for-loop-fails-only-on-last-iteration?rq=1
            print("Completed cost distance for OID %s at %s" % (row[0], datetime.datetime.now()))
            arcpy.AddMessage ("Completed cost distance for OID %s at %s" % (row[0], datetime.datetime.now()))
            print(".........................................................")
            arcpy.AddMessage (".........................................................")
            arcpy.AddMessage ("\n")
            
        del cursor

    # End time
    end = datetime.datetime.now()
    print("Cost dist calculation ended at %s" % end)
    arcpy.AddMessage ("Cost dist calculation ended at %s" % end)
    arcpy.AddMessage('\n')
    time_elapsed = end - start
    print("Time elapsed %s" % (time_elapsed))
    arcpy.AddMessage ("Time elapsed %s" % time_elapsed)
    arcpy.AddMessage ("\n")
    print(".........................................................")
    arcpy.AddMessage (".........................................................")
    arcpy.AddMessage ("\n")