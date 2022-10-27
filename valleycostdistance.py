# Import system modules  
import arcpy  
from arcpy import env  
import os  
import datetime

def valley(riv_in, wet_in, cd, outp, val):
    
    # Start time 
    start = datetime.datetime.now()
    print("Valley extraction started at %s" % start)
    arcpy.AddMessage ("Valley extraction started at %s" % start)
    arcpy.AddMessage ("\n")
    
    # Check out spatial extention
    arcpy.CheckOutExtension("Spatial") 
    
    # Set environment settings
    arcpy.ResetEnvironments ()
    env.workspace = cd
    env.scratchWorkspace = "in_memory"
    env.overwriteOutput = True
    
    # Get a list of the rasters in the workspace  
    rasters = arcpy.ListRasters("*")  
    
    # If code is stuck and would like to continue then uncomment these codes
#    rasters.sort()
#    rasters_sub = rasters[54:] # if you want to pick up where you left off (start a number before)
    
    # Dissolve wetland layer
    wetdis = "wetdis"
    arcpy.Dissolve_management(wet_in, os.path.join(outp, wetdis), "", "", "", "")
    
    # Loop through the list of rasters  
    for inRaster in rasters: # change here if you desire to continue from where you left (raster_sub)
        
        # Workspace containing cost distance rasters
        env.workspace = cd
        
        # Check that cd rasters have values
        check = arcpy.sa.Raster (inRaster).maximum
        if isinstance(check, float):
            
            # Get OID number
            num = int("".join(filter(str.isdigit, inRaster)))
            field = arcpy.Describe(os.path.join(outp, "cat_riv")).OIDFieldName
    #        field_short = field[0:3]
            
            # Select respective catchment
            print("Selected catchment %s at %s" % (num, datetime.datetime.now()))
            arcpy.AddMessage ("Selected catchment %s" % num)
            arcpy.AddMessage ("\n")
            attr_selection = arcpy.SelectLayerByAttribute_management(os.path.join(outp, "cat_riv"), "NEW_SELECTION", "%s = %s" % (field, num), None)
            
            # Extract rivers
            rivers = "rivers_" + "%s" % (num)
            arcpy.Clip_analysis(riv_in, attr_selection, os.path.join(outp, rivers), "")
            print("Rivers extracted for OID %s at %s" % (inRaster, datetime.datetime.now()))
            
            # Check if any wetlands are available for calibration
            arcpy.Intersect_analysis([os.path.join(outp, rivers), os.path.join(outp, wetdis)], os.path.join(outp, "checkint"), "ALL", None, "INPUT")
            numrows = int((arcpy.GetCount_management (os.path.join(outp, "checkint"))).getOutput(0))
                        
            if numrows > 0:
                
                print("Calibration wetlands available for OID %s at %s" % (inRaster, datetime.datetime.now()))
                
                # Get points on river
                rivpts = "rivpts_" + "%s" % (num)
                arcpy.GeneratePointsAlongLines_management(os.path.join(outp, rivers), os.path.join(outp, rivpts), "DISTANCE", "100 Unknown", None, "END_POINTS")
                print("Points on river extracted for OID %s at %s" % (inRaster, datetime.datetime.now()))
                
                # Create thiessen polygons
                thies = "thies_" + "%s" % (num)
                thiesmsk = "thiesmsk_" + "%s" % (num)
                arcpy.CreateThiessenPolygons_analysis(os.path.join(outp, rivpts), os.path.join(outp, thies), "ONLY_FID")
                arcpy.Clip_analysis(os.path.join(outp, thies), attr_selection, os.path.join(outp, thiesmsk), "")
                print("Thiessen polygons computed for OID %s at %s" % (inRaster, datetime.datetime.now()))
                
                # Clip out wetland layer
                wetclip = "wetclip_" + "%s" % (num)
                arcpy.Clip_analysis(os.path.join(outp, wetdis), attr_selection, os.path.join(outp, wetclip), "")
                print("Wetlands clipped out for OID %s at %s" % (inRaster, datetime.datetime.now()))
                del attr_selection
                
                # Split wetlands
                splitwet = "splitwet_" + "%s" % (num)
                arcpy.Clip_analysis(os.path.join(outp, thiesmsk), os.path.join(outp, wetclip), os.path.join(outp, splitwet), None)
                print("Wetland split completed for OID %s at %s" % (inRaster, datetime.datetime.now()))
                
                # Multipart to Singlepart
                singwet = "singwet_" + "%s" % (num)
                arcpy.MultipartToSinglepart_management(os.path.join(outp, splitwet), os.path.join(outp, singwet))
                print("Multi to singlepart completed for OID %s at %s" % (inRaster, datetime.datetime.now()))
                
                # Extract wetlands that's within extent of rivers
                wetriv = "wetriv_" + "%s" % (num)
                arcpy.SpatialJoin_analysis(os.path.join(outp, singwet), os.path.join(outp, rivers), os.path.join(outp, wetriv), "", "KEEP_COMMON", "", "INTERSECT", "", "")
                print("Wetlands within rivers extracted for OID %s at %s" % (inRaster, datetime.datetime.now()))
                
                # Extract cost distance values using wetlands
                wetcd = "wetcd_" + "%s" % (num)
                env.mask = os.path.join(outp, wetriv)
                con = arcpy.sa.Con(inRaster, inRaster, None, "VALUE > 0 And VALUE <= 500"); 
                con.save(os.path.join(outp, wetcd))
                
                # Check for zero cd rasters
                check2 = arcpy.sa.Raster (os.path.join(outp, wetcd)).maximum
                if isinstance(check2, float):
                    
                    print("Calibration wetlands coincide within rivers for OID %s at %s" % (inRaster, datetime.datetime.now()))
                                
                    arcpy.ClearEnvironment("mask")
                    meanResult = arcpy.GetRasterProperties_management (os.path.join(outp, wetcd), "MEAN", "")
                    mean = str(meanResult.getOutput(0))
                    print("Cost distance accumulation within wetlands extracted for OID %s at %s" % (inRaster, datetime.datetime.now()))
                    
                    # Extract valley from estimate made from wetland layer
                    print("Cutoff cost distance for OID %s is %s" % (inRaster, mean))
                    valR = "valR_" + "%s" % (num)
                    valley = arcpy.sa.Con(inRaster, 1, None, "VALUE <=" + mean); 
                    valley.save(os.path.join(outp, valR))
                    print("Valley extracted for OID %s at %s" % (inRaster, datetime.datetime.now()))
                    
                    # Convert raster to polygon
                    valP = "valP_" + "%s" % (num)
                    arcpy.conversion.RasterToPolygon(os.path.join(outp, valR), os.path.join(outp, valP), "SIMPLIFY", "Value", "SINGLE_OUTER_PART", None)
                    print("Completed conversion to polygon for OID %s at %s" % (inRaster, datetime.datetime.now()))
                    
                    # Make sure that rasters are saved before the next loop
                    con = None
                    valley = None
                    
                    print("Completed valley extraction for OID %s at %s" % (inRaster, datetime.datetime.now()))
                    arcpy.AddMessage ("Completed valley extraction for OID %s at %s" % (inRaster, datetime.datetime.now()))
                    arcpy.AddMessage('\n')
                    print(".........................................................")
                    arcpy.AddMessage (".........................................................")
                    arcpy.AddMessage ("\n")
                    
                else:
                    print("Calibration wetlands do not coincide with rivers for OID %s at %s" % (inRaster, datetime.datetime.now()))
                    continue
                
            else:
                print("No calibration wetlands available for OID %s at %s" % (inRaster, datetime.datetime.now()))
                continue
        
        else:
            continue       
        
    # Find all delineated river valleys  
    env.workspace = outp
    all_val = arcpy.ListFeatureClasses("val*")
    
    # Merge all delineated river valleys
    mer = "mer"
    arcpy.Merge_management (all_val, os.path.join(outp, mer))
    print("Completed merging river valleys at %s" % datetime.datetime.now())
    arcpy.AddMessage ("Completed merging river valleys at %s" % datetime.datetime.now())
    arcpy.AddMessage ("\n")
    
    # Dissolve river valleys
    arcpy.Dissolve_management (os.path.join(outp, mer), val, "", "", "", "")
    print("Completed dissolving river valleys at %s" % datetime.datetime.now())
    arcpy.AddMessage ("Completed dissolving river valleys at %s" % datetime.datetime.now())
    arcpy.AddMessage ("\n")
    
    # End time
    end = datetime.datetime.now()
    print("Valley extraction ended at %s" % end)
    arcpy.AddMessage ("Valley extraction ended at %s" % end)
    arcpy.AddMessage ("\n")
    time_elapsed = end - start
    print("Time elapsed %s" % (time_elapsed))
    arcpy.AddMessage ("Time elapsed %s" % time_elapsed)
    arcpy.AddMessage ("\n")