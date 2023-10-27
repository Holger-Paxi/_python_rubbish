####################
"""
Double-click on the history item or paste the command below to re-run the algorithm
"""

processing.run(
    "native:polygonfromlayerextent", {
        'INPUT':'/home/holger/Downloads/_rubbish/_python_rubbish/sc__0001_____CA_1__0000.gpkg|layername=sc__0001_____CA_1__0000',
        'ROUND_TO':0,
        'OUTPUT':'/home/holger/Downloads/_rubbish/_python_rubbish/extent_polygon.gpkg'
        })




###################
"""
Double-click on the history item or paste the command below to re-run the algorithm
"""

processing.run(
    "saga:thinplatespline", {
        'SHAPES':'/home/holger/Downloads/_rubbish/_python_rubbish/ts_199905052245_020980.gpkg|layername=ts_199905052245_020980',
        'FIELD':'Depth',
        'REGULARISATION':0.0001,
        'SEARCH_RANGE':1,
        'SEARCH_RADIUS':20000,
        'SEARCH_POINTS_ALL':1,
        'SEARCH_POINTS_MIN':16,
        'SEARCH_POINTS_MAX':20,
        'SEARCH_DIRECTION':0,
        'TARGET_USER_XMIN TARGET_USER_XMAX TARGET_USER_YMIN TARGET_USER_YMAX':'332324.750000000,332375.875000000,6247078.500000000,6247184.500000000 [EPSG:28356]',
        'TARGET_USER_SIZE':1,
        'TARGET_USER_FITS':0,
        'TARGET_TEMPLATE':None,
        'TARGET_OUT_GRID':'/home/holger/Downloads/_rubbish/_python_rubbish/get_raster_TPS_surface.sdat'
        })



#################
#################

"""
Double-click on the history item or paste the command below to re-run the algorithm
"""

processing.run(
    "gdal:translate", {
        'INPUT':'/home/holger/Downloads/_rubbish/_python_rubbish/get_raster_TPS_surface.sdat',
        'TARGET_CRS':None,
        'NODATA':None,
        'COPY_SUBDATASETS':False,
        'OPTIONS':'',
        'EXTRA':'',
        'DATA_TYPE':0,
        'OUTPUT':'/home/holger/Downloads/_rubbish/_python_rubbish/translate_get_raster_TPS_surface.gpkg'
        })


#####################
"""
Double-click on the history item or paste the command below to re-run the algorithm
"""

processing.run(
    "gdal:cliprasterbymasklayer", {
        'INPUT':'/home/holger/Downloads/_rubbish/_python_rubbish/get_raster_TPS_surface.sdat',
        'MASK':'/home/holger/Downloads/_rubbish/_python_rubbish/sc__0001_____CA_1__0000.gpkg|layername=sc__0001_____CA_1__0000',
        'SOURCE_CRS':None,
        'TARGET_CRS':None,
        'NODATA':None,
        'ALPHA_BAND':False,
        'CROP_TO_CUTLINE':True,
        'KEEP_RESOLUTION':False,
        'SET_RESOLUTION':False,
        'X_RESOLUTION':None,
        'Y_RESOLUTION':None,
        'MULTITHREADING':False,
        'OPTIONS':'',
        'DATA_TYPE':0,
        'EXTRA':'',
        'OUTPUT':'/home/holger/Downloads/_rubbish/_python_rubbish/clip_raster_layer.gpkg'
        })



######################
"""
Double-click on the history item or paste the command below to re-run the algorithm
"""

processing.run(
    "native:rastersurfacevolume", {
        'INPUT':'/home/holger/Downloads/_rubbish/_python_rubbish/clip_raster_layer.gpkg',
        'BAND':1,
        'LEVEL':0,
        'METHOD':0,
        'OUTPUT_TABLE':'/home/holger/Downloads/_rubbish/_python_rubbish/calculate_raster_volume.gpkg'
        })




#####################
"""
Double-click on the history item or paste the command below to re-run the algorithm
"""

processing.run(
    "saga:realsurfacearea", {
        'DEM':'/home/holger/Downloads/_rubbish/_python_rubbish/clip_raster_layer.gpkg',
        'AREA':'/home/holger/Downloads/_rubbish/_python_rubbish/get_raster_area.sdat'
        })




######################
######################

"""
Double-click on the history item or paste the command below to re-run the algorithm
"""

processing.run(
    "gdal:translate", {
        'INPUT':'/home/holger/Downloads/_rubbish/_python_rubbish/get_raster_area.sdat',
        'TARGET_CRS':None,
        'NODATA':None,
        'COPY_SUBDATASETS':False,
        'OPTIONS':'',
        'EXTRA':'',
        'DATA_TYPE':0,
        'OUTPUT':'/home/holger/Downloads/_rubbish/_python_rubbish/translate_get_raster_area.gpkg'
        })


##########################
"""
Double-click on the history item or paste the command below to re-run the algorithm
"""

processing.run(
    "native:rastersurfacevolume", {
        'INPUT':'/home/holger/Downloads/_rubbish/_python_rubbish/get_raster_area.sdat',
        'BAND':1,
        'LEVEL':0,
        'METHOD':0,
        'OUTPUT_TABLE':'/home/holger/Downloads/_rubbish/_python_rubbish/calculate_raster_area.gpkg'
        })

