# %%
import sys
import math
from csv import DictWriter
import datetime as dt

# %%
from qgis.core import *
# from PyQt5.QtCore import QCoreApplication
# from qgis.core import (
#     QgsProcessing,
#     QgsProcessingAlgorithm,
#     QgsProcessingParameterFeatureSource,
#     QgsProcessingParameterRasterDestination
#     )

# from qgis.analysis import QgsNativeAlgorithms

# sys.path.append('/usr/lib/qgis/plugins')
sys.path.append('/usr/share/qgis/python/plugins')
# sys.path.append('/usr/share/saga/python/plugins')




# import processing
# QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

# %%
def main():

    # from processing.algs.qgis.
    # %%
    # Supply path to qgis install location
    QgsApplication.setPrefixPath("/usr", True)

    # %%
    # Create a reference to the QgsApplication.  Setting the
    # second argument to False disables the GUI.
    qgs = QgsApplication([], False)

    # %%
    # Load providers
    qgs.initQgis()

    # %%


    import processing
    from processing.core.Processing import Processing
    Processing.initialize()

    # Processing.updateAlgsList()
    # QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
    # QgsApplication.processingRegistry().algorithms()



    # %%
    # Write your code here to load some layers, use processing
    # algorithms, etc.
    point = 'ts_199905052245_020980.gpkg'
    geome = 'sc__0001_____CA_1__0000.gpkg'
    arg_cell_size = 1



    t = dt.datetime.now()
    # extent_polygon
    arg_extent_pol_path_file = processing.run(
        "native:polygonfromlayerextent", {
            'INPUT':geome, 
            'ROUND_TO':0, 
            # 'OUTPUT':'./_sa_extent_polygon.gpkg'
            ## 'OUTPUT':'./_sa_extent_polygon.shp'
            'OUTPUT':'TEMPORARY_OUTPUT'
            })
    arg_extent_pol_path_file = arg_extent_pol_path_file['OUTPUT']
    print('extent_polygon {}'.format(dt.datetime.now() - t))


    t = dt.datetime.now()
    # get_raster_TPS_surface
    ###### GPKG
    # minx = math.floor(QgsVectorLayer(arg_extent_pol_path_file).getFeature(1)[1]) - 2*arg_cell_size
    # miny = math.floor(QgsVectorLayer(arg_extent_pol_path_file).getFeature(1)[2]) - 2*arg_cell_size
    # maxx = math.ceil(QgsVectorLayer(arg_extent_pol_path_file).getFeature(1)[3]) + 2*arg_cell_size
    # maxy = math.ceil(QgsVectorLayer(arg_extent_pol_path_file).getFeature(1)[4]) + 2*arg_cell_size
    ######## SHP
    # minx = math.floor(QgsVectorLayer(arg_extent_pol_path_file).getFeature(0)[0]) - 2*arg_cell_size
    # miny = math.floor(QgsVectorLayer(arg_extent_pol_path_file).getFeature(0)[1]) - 2*arg_cell_size
    # maxx = math.ceil(QgsVectorLayer(arg_extent_pol_path_file).getFeature(0)[2]) + 2*arg_cell_size
    # maxy = math.ceil(QgsVectorLayer(arg_extent_pol_path_file).getFeature(0)[3]) + 2*arg_cell_size
    ####### tmp
    minx = math.floor(arg_extent_pol_path_file.getFeature(1)[0]) - 2*arg_cell_size
    miny = math.floor(arg_extent_pol_path_file.getFeature(1)[1]) - 2*arg_cell_size
    maxx = math.ceil(arg_extent_pol_path_file.getFeature(1)[2]) + 2*arg_cell_size
    maxy = math.ceil(arg_extent_pol_path_file.getFeature(1)[3]) + 2*arg_cell_size
    ############
    crs_proj = '[EPSG:28356]'
    arg_TPS_surface_path_file = processing.run(
        "saga:thinplatespline", {
            'SHAPES':point, 
            'FIELD':'Depth', 
            'REGULARISATION':0.0001,
            'SEARCH_RANGE':1,
            'SEARCH_RADIUS':20000,
            'SEARCH_POINTS_ALL':1,
            'SEARCH_POINTS_MIN':16,
            'SEARCH_POINTS_MAX':20,
            'SEARCH_DIRECTION':0,
            'TARGET_USER_XMIN TARGET_USER_XMAX TARGET_USER_YMIN TARGET_USER_YMAX':'{:.9f},{:.9f},{:.9f},{:.9f} {}'.format(minx, maxx, miny, maxy, crs_proj),
            'TARGET_USER_SIZE':arg_cell_size,
            'TARGET_USER_FITS':0,
            'TARGET_TEMPLATE':None,
            # 'TARGET_OUT_GRID':'./_sa_get_raster_TPS_surface.sdat'
            'TARGET_OUT_GRID':'TEMPORARY_OUTPUT'
            })
    arg_TPS_surface_path_file = arg_TPS_surface_path_file['TARGET_OUT_GRID']
    print('get_raster_TPS_surface {}'.format(dt.datetime.now() - t))



    t = dt.datetime.now()
    # clip_raster_layer
    arg_clip_TPS_raster_path_file = processing.run(
        "gdal:cliprasterbymasklayer", {
            'INPUT':arg_TPS_surface_path_file, 
            'MASK':geome,
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
            'OUTPUT':'TEMPORARY_OUTPUT'
            # 'OUTPUT':'./_sa_clip_raster_layer.gpkg'
            })
    arg_clip_TPS_raster_path_file = arg_clip_TPS_raster_path_file['OUTPUT']
    print('clip_raster_layer {}'.format(dt.datetime.now() - t))



    t = dt.datetime.now()
    # calculate_raster_volume
    arg_calculate_raster_volume_path_file = processing.run(
        "native:rastersurfacevolume", {
            'INPUT':arg_clip_TPS_raster_path_file, 
            'BAND':1, 
            'LEVEL':0, 
            'METHOD':0, 
            'OUTPUT_TABLE':'TEMPORARY_OUTPUT'
            # 'OUTPUT_TABLE':'./_sa_calculate_raster_volume.gpkg'
            }) 
    arg_calculate_raster_volume_path_file = arg_calculate_raster_volume_path_file['VOLUME']
    print('calculate_raster_volume {}'.format(dt.datetime.now() - t))



    t = dt.datetime.now()
    # get_raster_area
    arg_get_raster_area_path_file = processing.run(
        "saga:realsurfacearea", {
            'DEM':arg_clip_TPS_raster_path_file, 
            'AREA':'TEMPORARY_OUTPUT'
            # 'AREA':'./_sa_get_raster_area.sdat'
            })
    arg_get_raster_area_path_file = arg_get_raster_area_path_file['AREA']
    print('get_raster_area {}'.format(dt.datetime.now() - t))



    t = dt.datetime.now()
    # calculate_raster_area
    arg_calculate_raster_area_path_file = processing.run(
        "native:rastersurfacevolume", {
            'INPUT':arg_get_raster_area_path_file, 
            'BAND':1, 
            'LEVEL':0, 
            'METHOD':0, 
            'OUTPUT_TABLE':'TEMPORARY_OUTPUT'
            # 'OUTPUT_TABLE':'./_sa_calculate_raster_area.gpkg'
            })
    arg_calculate_raster_area_path_file = arg_calculate_raster_area_path_file['AREA']
    print('calculate_raster_area {}'.format(dt.datetime.now() - t))



    t = dt.datetime.now()
    # calculate_precipitation
    precipitation = (arg_calculate_raster_volume_path_file / arg_calculate_raster_area_path_file 
        if arg_calculate_raster_area_path_file != 0 else 0)
    prec_keys = [
        # 'sub_catchment_ID', 
        # 'sub_catchment', 
        # 'timestamp_ID', 
        # 'timestamp', 
        'prec_depth', 
        'volume', 
        'area'
        ]
    prec_dict = {
        # 'sub_catchment_ID': arg_pol_name_index,
        # 'sub_catchment': arg_pol_path_file.split('/')[-1].split('\\')[-1].split('.')[0], 
        # 'timestamp_ID': arg_point_name_index,
        # 'timestamp': arg_point_path_file.split('/')[-1].split('\\')[-1].split('_')[1], 
        'prec_depth': precipitation, 
        'volume': arg_calculate_raster_volume_path_file, 
        'area': arg_calculate_raster_area_path_file
        }
    # prec_file = arg_container_dir + arg_pol_path_file.split('/')[-1].split('\\')[-1].split('.')[0] + '.csv'
    prec_file = './_sa_calculate_precipitation.csv'
    with open(prec_file, 'a+', newline='') as csv_file:
        record_writer = DictWriter(csv_file, fieldnames=prec_keys)
        record_writer.writerow(prec_dict)
    print('calculate_precipitation {}'.format(dt.datetime.now() - t))





    # %%
    # Finally, exitQgis() is called to remove the
    # provider and layer registries from memory
    qgs.exitQgis()




if __name__ == '__main__':
    main()