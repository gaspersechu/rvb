# Import system modules
import arcpy
from arcpy import env
import os
import datetime

def slope(riv_in, cat_in, ras_in, outp):
    
    # Start time 
    start = datetime.datetime.now()
    print("Slope calculation started at %s" % start)
    arcpy.AddMessage ("Slope calculation started at %s" % start)
    arcpy.AddMessage ("\n")
    
    # Select features that intersect
    catch = os.path.join(outp, "cat_riv")
    selection = arcpy.SelectLayerByLocation_management(cat_in, "INTERSECT", riv_in, None, "NEW_SELECTION", "NOT_INVERT")
    arcpy.CopyFeatures_management(selection, catch, None, None, None, None)
    
    # Scratch workspace
    ras = arcpy.Raster(ras_in)
    env.scratchWorkspace = "in_memory"
    env.cellSize = ras
    env.snapRaster = ras
    env.mask = catch
    
    # Calculating slope
    slope = arcpy.sa.Slope (ras, "DEGREE", None, None, "METER"); 
    slope.save(os.path.join(outp, "slope"))
    print("Completed calculating slope at %s" % datetime.datetime.now())
    arcpy.AddMessage ("Completed calculating slope at %s" % datetime.datetime.now())
    arcpy.AddMessage ("\n")
    
    # Replacing 0 slope values with 0.0000000001
    env.extent = "MAXOF"
    con_slope = arcpy.sa.Con(slope, 0.0000000001, slope, "VALUE = 0"); 
    con_slope.save(os.path.join(outp, "con_slope"))
    print("Completed replacing zeros at %s" % datetime.datetime.now())
    arcpy.AddMessage ("Completed replacing zeros at %s" % datetime.datetime.now())
    arcpy.AddMessage ("\n")
    
    # End time
    end = datetime.datetime.now()
    print("Slope calculation ended at %s" % end)
    arcpy.AddMessage ("Slope calculation ended at %s" % end)
    arcpy.AddMessage ("\n")
    time_elapsed = end - start
    print("Time elapsed %s" % (time_elapsed))
    arcpy.AddMessage ("Time elapsed %s" % time_elapsed)
    arcpy.AddMessage ("\n")
    print(".........................................................")
    arcpy.AddMessage (".........................................................")
    arcpy.AddMessage ("\n")