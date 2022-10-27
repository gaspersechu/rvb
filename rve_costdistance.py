""" Title:
        River valley bottom delineation using cost distance accumulation

    Author:
        Gasper Sechu (gasper.sechu@gmail.com)
        Aarhus University, Denmark
        
"""

# Import modules
import arcpy
import os
from pathlib import Path
import datetime
from slope import slope
from valleycostdistance import valley
from costdistance import costdist

# Starting script
start = datetime.datetime.now()
print("Script started at %s" % start)
arcpy.AddMessage ("Script started started at %s" % start)
arcpy.AddMessage ("\n")

# Check out spatial extention
arcpy.CheckOutExtension("Spatial")

# Environments
arcpy.env.overwriteOutput = True

# Python inputs
#riv =  r"D:\PhD\Study1\Inputs\rivers.shp" # river network as a shapefile
#cat = r"D:\PhD\Study1\Inputs\catchments.shp" # catchments as a shapefile
#dem = r"D:\PhD\Study1\Inputs\DHyM.tif" # elevation model as a raster
#wet = r"D:\PhD\Study1\Inputs\wetlands.shp" # measured valley bottom, wetlands or any wet signature in low areas
#pth = r"D:\PhD\Study1\Outputs\river_valley_bottom_dk" # path to outputs (scratch and cost distance folders)
#outval = r"D:\PhD\Study1\Outputs\river_valley_bottom_dk\outputs.gdb\rvb_dk" # path to output river valley

# ArcGIS inputs
riv =  arcpy.GetParameterAsText(0) # river network as a shapefile
cat = arcpy.GetParameterAsText(1) # catchments as a shapefile
dem = arcpy.GetParameterAsText(2) # elevation model as a raster
wet = arcpy.GetParameterAsText(3) # measured river valley
pth = arcpy.GetParameterAsText(4) # path to outputs (scratch and cost distance folders)
outval = arcpy.GetParameterAsText(5) # path to output river valley

# Check to see if scratch geodatabase exists
s = Path(os.path.join(pth, "outputs.gdb"))
if s.exists() == False:
    scrg = arcpy.CreateFileGDB_management(pth, "outputs")
    scr = scrg.getOutput(0) # scratch folder
else:
    scr = os.path.join(pth, "outputs.gdb") #scr = r"in_memory" (if you want to store in memory)

# Check to see if cost dist folder exists (use code in comments if you want results in a folder instead of gdb)
c = Path(os.path.join(pth, "costdist.gdb")) # Path(os.path.join(pth, "costdist"))
if c.exists() == False:
    cstg = arcpy.CreateFileGDB_management(pth, "costdist")  # arcpy.CreateFolder_management(pth, "costdist")
    cst = cstg.getOutput(0) # cost distance folder
else:
    cst = os.path.join(pth, "costdist.gdb") # os.path.join(pth, "costdist")

# Calculate slope and replace 0 slopes with small value
slope(riv, cat, dem, scr)

# Cost distance calculation
costdist(riv, cat, os.path.join(scr, "con_slope"), cst, scr)

# Extract valley
valley(riv, wet, cst, scr, outval)

# Ending script
end = datetime.datetime.now()
print("Script ended at %s" % end)
arcpy.AddMessage ("Script ended at %s" % end)
arcpy.AddMessage ("\n")
time_elapsed = end - start
print("Time elapsed %s" % (time_elapsed))
arcpy.AddMessage ("Time elapsed %s" % time_elapsed)
arcpy.AddMessage ("\n")
print(".........................................................")
arcpy.AddMessage (".........................................................")
arcpy.AddMessage ("\n")