# %%
import sys
import math
from csv import DictWriter
import datetime as dt

from qgis.core import *
sys.path.append('/usr/share/qgis/python/plugins')

# Supply path to qgis install location
QgsApplication.setPrefixPath("/usr", True)

# Create a reference to the QgsApplication. Setting the
# second argument to False disables the GUI.
qgs = QgsApplication([], False)

# Load providers
qgs.initQgis()

# Dependencies
import processing
from processing.core.Processing import Processing
Processing.initialize()

# %%
def main():

    # # Supply path to qgis install location
    # QgsApplication.setPrefixPath("/usr", True)

    # # Create a reference to the QgsApplication. Setting the
    # # second argument to False disables the GUI.
    # qgs = QgsApplication([], False)

    # # Load providers
    # qgs.initQgis()

    # # Dependencies
    # # import processing
    # from processing.core.Processing import Processing
    # Processing.initialize()

    # Write your code here to load some layers, use processing
    # algorithms, etc.
    arg_point_name = 'ts_199905052245_020980.gpkg'
    arg_polygon_name = 'sc__0001_____CA_1__0000.gpkg'
    arg_cell_size = 1

    arg_extent_pol_path_file = extent_polygon(arg_polygon_name)
    arg_TPS_surface_path_file = get_raster_TPS_surface(arg_point_name, arg_extent_pol_path_file, arg_cell_size)
    arg_clip_TPS_raster_path_file = clip_raster_layer(arg_polygon_name, arg_TPS_surface_path_file)
    arg_calculate_raster_volume_path_file = calculate_raster_volume(arg_clip_TPS_raster_path_file)
    arg_get_raster_area_path_file = get_raster_area(arg_clip_TPS_raster_path_file)
    arg_calculate_raster_area_path_file = calculate_raster_area(arg_get_raster_area_path_file)
    calculate_precipitation(
        arg_calculate_raster_volume_path_file, 
        arg_calculate_raster_area_path_file, 
        # arg_index_polygon_name,
        # arg_polygon_name, 
        # arg_index_point_name,
        # arg_point_name, 
        # arg_container_name
        )


    # # Finally, exitQgis() is called to remove the
    # # provider and layer registries from memory
    # qgs.exitQgis()


# %%
def extent_polygon(arg_pol_path_file):
    t = dt.datetime.now()
    # extent_polygon
    arg_extent_pol_path_file = processing.run(
        "native:polygonfromlayerextent", {
            'INPUT':arg_pol_path_file, 
            'ROUND_TO':0, 
            # 'OUTPUT':'./_sa_extent_polygon.gpkg'
            ## 'OUTPUT':'./_sa_extent_polygon.shp'
            'OUTPUT':'TEMPORARY_OUTPUT'
            })
    print('extent_polygon {}'.format(dt.datetime.now() - t))
    return arg_extent_pol_path_file['OUTPUT']

# %%
def get_raster_TPS_surface(arg_point_path_file, arg_extent_pol_path_file, arg_cell_size):
    t = dt.datetime.now()
    # get_raster_TPS_surface
    ###### GPKG
    # minx = math.floor(QgsVectorLayer(arg_extent_pol_path_file).getFeature(1)[1]) - 2*arg_cell_size
    # miny = math.floor(QgsVectorLayer(arg_extent_pol_path_file).getFeature(1)[2]) - 2*arg_cell_size
    # maxx = math.ceil(QgsVectorLayer(arg_extent_pol_path_file).getFeature(1)[3]) + 2*arg_cell_size
    # maxy = math.ceil(QgsVectorLayer(arg_extent_pol_path_file).getFeature(1)[4]) + 2*arg_cell_size
    ####### tmp
    minx = math.floor(arg_extent_pol_path_file.getFeature(1)[0]) - 2*arg_cell_size
    miny = math.floor(arg_extent_pol_path_file.getFeature(1)[1]) - 2*arg_cell_size
    maxx = math.ceil(arg_extent_pol_path_file.getFeature(1)[2]) + 2*arg_cell_size
    maxy = math.ceil(arg_extent_pol_path_file.getFeature(1)[3]) + 2*arg_cell_size
    ############
    crs_proj = '[EPSG:28356]'
    arg_TPS_surface_path_file = processing.run(
        "saga:thinplatespline", {
            'SHAPES':arg_point_path_file, 
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
    print('get_raster_TPS_surface {}'.format(dt.datetime.now() - t))
    return arg_TPS_surface_path_file['TARGET_OUT_GRID']

# %%
def clip_raster_layer(arg_pol_path_file, arg_TPS_surface_path_file):
    t = dt.datetime.now()
    # clip_raster_layer
    arg_clip_TPS_raster_path_file = processing.run(
        "gdal:cliprasterbymasklayer", {
            'INPUT':arg_TPS_surface_path_file, 
            'MASK':arg_pol_path_file,
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
    print('clip_raster_layer {}'.format(dt.datetime.now() - t))
    return arg_clip_TPS_raster_path_file['OUTPUT']

# %%
def calculate_raster_volume(arg_clip_TPS_raster_path_file):
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
    print('calculate_raster_volume {}'.format(dt.datetime.now() - t))
    return arg_calculate_raster_volume_path_file['VOLUME']

# %%
def get_raster_area(arg_clip_TPS_raster_path_file):
    t = dt.datetime.now()
    # get_raster_area
    arg_get_raster_area_path_file = processing.run(
        "saga:realsurfacearea", {
            'DEM':arg_clip_TPS_raster_path_file, 
            'AREA':'TEMPORARY_OUTPUT'
            # 'AREA':'./_sa_get_raster_area.sdat'
            })
    print('get_raster_area {}'.format(dt.datetime.now() - t))
    return arg_get_raster_area_path_file['AREA']

# %%
def calculate_raster_area(arg_get_raster_area_path_file):
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
    print('calculate_raster_area {}'.format(dt.datetime.now() - t))
    return arg_calculate_raster_area_path_file['AREA']

# %%
def calculate_precipitation(
    arg_calculate_raster_volume_path_file, 
    arg_calculate_raster_area_path_file, 
    # arg_pol_name_index,
    # arg_pol_path_file, 
    # arg_point_name_index,
    # arg_point_path_file, 
    # arg_container_dir
    ):
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
if __name__ == '__main__':
    main()


# Finally, exitQgis() is called to remove the
# provider and layer registries from memory
qgs.exitQgis()