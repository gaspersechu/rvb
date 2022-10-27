# River Valley Bottom Delineation Tool
River valley delineation script from the publication:
A Stepwise GIS Approach for the Delineation of River Valley Bottom within Drainage Basins Using a Cost Distance Accumulation Analysis

## Instructions
You can easily use the toolbox RVBD.tbx with ArcGIS Pro. However, if you decide to use it as a script, then use the Python script rve_costdistance.py. This calls the scripts slope.py, costdistance.py, and valleycostdistance.py. If you go this route, you need to uncomment the inputs under “Python inputs” found in rve_costdistance.py, and replace the directories with paths to your data. Likewise, turn the code under “ArcGIS inputs” into comments.

## Reference
https://doi.org/10.3390/w13060827