# %% MODULES AND PACKAGES
# importing modules
import pandas as pd
import processing
import numpy as np
import geopandas as gpd
import time
import datetime as dt
from csv import DictWriter

# from qgis.core import *
# import qgis.utils

# %% STARTING TIME
starting_time = time.time()


# %% FUNCTIONS THAT RUN

def Get_Vol_Area_shp(df_sc_index_2, temp_var_clip_sdat_file_loc, ts_name_GivenIndex_2):          # (df_sc_index_2):          # (df_sc_index_2, temp_var_clip_sdat_file_loc)
# arg1: each row index in dataframe Arg_SC_dt_index; it is a dataframe
# arg2: only one sdat file produced by Arg_TS_dt_index in process; it is a variable which refers the file location
# arg3: only one temporary timestamp name for the sdat file given the index of the timestamp in process: it is a variable which refers the timestamp name given an index

    # CLIPPING SUBCATCHMENTS
    # Selection and clipping of each subcatchment

    # input variables for clipping subcatchments
    in_sc_sdat_file = temp_var_clip_sdat_file_loc                    #temp_var_clip_sdat_file_loc       # exe_clp['OUTPUT']
    mask_sc_shp_file = '{}{}.shp'.format(loc_sc_folder, sc_name.iloc[df_sc_index_2,0])
    # out_clip_sc_sdat_file = '{}{}_{}.sdat'.format(out_folder, ts_name.iloc[0,0], sc_name.iloc[0,0])

    # CRBML via QGIS processing
    exe_clp_sc = processing.run("gdal:cliprasterbymasklayer",\
        {'INPUT':in_sc_sdat_file,\
        'MASK': mask_sc_shp_file,\
        'SOURCE_CRS':None,\
        'TARGET_CRS':None,\
        'NODATA':None,\
        'ALPHA_BAND':False,\
        'CROP_TO_CUTLINE':True,\
        'KEEP_RESOLUTION':False,\
        'SET_RESOLUTION':False,\
        'X_RESOLUTION':None,\
        'Y_RESOLUTION':None,\
        'MULTITHREADING':False,\
        'OPTIONS':'',\
        'DATA_TYPE':0,\
        'EXTRA':'',\
        'OUTPUT':'TEMPORARY_OUTPUT'})


    # GETTING VOLUME AND AREA
    # Getting the volume and area for each subcatchment to get the total depth

    # input variables for getting the volume and area
    in_va_sdat_file = exe_clp_sc['OUTPUT']
    temp_out_va_dbf_file = '{}temp_va.shp'.format(out_folder)

    # raster surface volume via QGIS processing                 # exe_va_sc = 
    processing.run("native:rastersurfacevolume",\
        {'INPUT':in_va_sdat_file,\
        'BAND':1,\
        'LEVEL':0,\
        'METHOD':0,\
    #    'OUTPUT_HTML_FILE':'TEMPORARY_OUTPUT',\
        'OUTPUT_TABLE':temp_out_va_dbf_file})                   # 'TEMPORARY_OUTPUT'
    

    # CALCULATING PRECIPITATION DEPTH
    # calculating precipitation depth (pd) from attribute table sdat file

    in_pd_dbf_file = '{}temp_va.dbf'.format(out_folder)             # temp_out_va_dbf_file           # exe_va_sc['OUTPUT_TABLE']
    attb_table = QgsVectorLayer(in_pd_dbf_file, '', 'ogr')
    first_feature_table = attb_table.getFeature(0)
    vol_mm_x_m2 = first_feature_table[0]
    area_m2 = first_feature_table[1]
    # prec_depth_mm = np.float64(vol_mm_x_m2) / area_m2
    prec_depth_mm = vol_mm_x_m2 / area_m2 if area_m2 != 0 else 0

    # timestamp in different format
    t_s = ts_name_GivenIndex_2[3:]
    time_stamp = dt.datetime.strptime(t_s, '%Y%m%d%H%M')

    # GETTING PRECIPITATION DEPTHS CSV FILES
    # Getting the precipitation depth (pd) for each subcatchment considering their timestamp, volume and area

    field_names = ['SUB_CATCHMENT_ID', 'TIMESTAMP', 'PRECIPITATION_DEPTH', 'VOLUME', 'AREA']
    out_pd_csv_file = '{}{}.csv'.format(out_folder, sc_name.iloc[df_sc_index_2,0])
    first_feature_record = {'SUB_CATCHMENT_ID': sc_name.iloc[df_sc_index_2,0],\
        'TIMESTAMP': time_stamp,\
        'PRECIPITATION_DEPTH': prec_depth_mm,\
        'VOLUME': vol_mm_x_m2,\
        'AREA': area_m2}

    with open(out_pd_csv_file, 'a+', newline='') as csv_file:
        record_writer = DictWriter(csv_file, fieldnames=field_names)
        record_writer.writerow(first_feature_record)


# %% #################################################

def Get_Simplified_Raster(df_ts_index_1, df_sc_index_1):
# arg1: each row index in dataframe Arg_TS_dt_index; it is a dataframe
# arg2: all dataframe indexes in Arg_SC_dt_index; it is a dataframe

    # POINT SHAPEFILE - PRECIPITACION DEPTH
    # loading point shape file having the precipitation depth for each timestamp

    point_shp_folder = 'C:/Users/13004522/Downloads/SharedFiles_ProfJames/Testing_Files/out/'
    point_shp_file = '{}{}.shp'.format(point_shp_folder, ts_name.iloc[df_ts_index_1,0])


    # THIN PLATE SURFACE
    # Generating the Thin Plate Surface (TPS) raster file (sdat file) by using processing

    # Input variables for TPS
    in_tps_shp_file = point_shp_file
    x_min = 331480.0
    x_max = 335660.0
    y_min = 6244860.0
    y_max = 6249400.0
    crs_shp = '[EPSG:28356]'
    cell_size = 1
    # out_tps_sdat_file = '{}{}_tps.sdat'.format(out_folder, ts_name.iloc[df_ts_index_1,0])

    # TPS via SAGA processing
    exe_tps = processing.run("sagang:thinplatespline",\
        {'SHAPES':in_tps_shp_file,\
        'FIELD':'Depth',\
        'TARGET_USER_XMIN TARGET_USER_XMAX TARGET_USER_YMIN TARGET_USER_YMAX':'{},{},{},{} {}'.format(x_min, x_max, y_min, y_max, crs_shp),\
        'TARGET_USER_SIZE':cell_size,\
        'TARGET_OUT_GRID':'TEMPORARY_OUTPUT',\
        'REGULARISATION':0.0001,\
        'SEARCH_RANGE':1,\
        'SEARCH_RADIUS':20000,\
        'SEARCH_POINTS_ALL':1,\
        'SEARCH_POINTS_MIN':16,\
        'SEARCH_POINTS_MAX':20,\
        'SEARCH_DIRECTION':0})


    # SET ZEROS INSTEAD OF NEGATIVE VALUES FOR TPS SURFACE
    # Changing negative values to zero via Raster calculator (RC)

    # Input variables for RC
    in_rc_sdat_file = exe_tps['TARGET_OUT_GRID']
    # out_rc_sdat_file = '{}{}_rc.sdat'.format(out_folder, ts_name.iloc[df_ts_index_1,0])

    # Raster calculator via QGIS processing
    exe_rc = processing.run("qgis:rastercalculator",\
        {'EXPRESSION':'("{0}@1">=0.0)*"{0}@1"'.format(in_rc_sdat_file),\
        'LAYERS':[in_rc_sdat_file],\
        'CELLSIZE':0,\
        'EXTENT':None,\
        'CRS':None,\
        'OUTPUT':'TEMPORARY_OUTPUT'})


    # CLIPPING TPS SURFACE
    # Clipping raster (CLP) by mask layer (the mask is a polygon shapefile)

    # Input variables for clipping raster by mask layer(CRBML)
    in_clp_sdat_file = exe_rc['OUTPUT']
    in_pol_shp_file = 'C:/Users/13004522/Downloads/SharedFiles_ProfJames/Rainfall_Data/modified_from_Siming/SubcatSJoutlet_GDA_MGA_boundary.shp'
    temp_out_clp_sdat_file = '{}temp_clp.sdat'.format(out_folder)         # out_clp_sdat_file = '{}{}_clp.sdat'.format(out_folder, ts_name.iloc[df_ts_index_1,0])

    # CRBML via QGIS processing                 # exe_clp = 
    processing.run("gdal:cliprasterbymasklayer",\
        {'INPUT':in_clp_sdat_file,\
        'MASK':in_pol_shp_file,\
        'SOURCE_CRS':None,\
        'TARGET_CRS':None,\
        'NODATA':None,\
        'ALPHA_BAND':False,\
        'CROP_TO_CUTLINE':True,\
        'KEEP_RESOLUTION':False,\
        'SET_RESOLUTION':False,\
        'X_RESOLUTION':None,\
        'Y_RESOLUTION':None,\
        'MULTITHREADING':False,\
        'OPTIONS':'',\
        'DATA_TYPE':0,\
        'EXTRA':'',\
        'OUTPUT':temp_out_clp_sdat_file})           # 'OUTPUT':'TEMPORARY_OUTPUT'})
    
    ts_name_GivenIndex = ts_name.iloc[df_ts_index_1,0]
    # out_clip_sdat = exe_clp['OUTPUT']

    # RUNNING THE FUNCTION Get_Vol_Area_shp

    df_sc_index_1.apply(lambda x: Get_Vol_Area_shp(x.sc_index, temp_out_clp_sdat_file, ts_name_GivenIndex), axis=1)
    # arg1: each row index in dataframe Arg_SC_dt_index; it is a dataframe
    # arg2: only one sdat file produced by Arg_TS_dt_index in process; it is a variable which refers the file location
    # arg3: only one temporary timestamp name for the sdat file given the index of the timestamp in process: it is a variable which refers the timestamp name given an index

    # Arg_SC_dt_index['loc_sdat_file'] = temp_out_clp_sdat_file
    # Arg_SC_dt_index['ts_index'] = ts_name_GivenIndex
    # Arg_SC_dt_index.apply(lambda x: Get_Vol_Area_shp(x.sc_index, temp_out_clp_sdat_file, ts_name_GivenIndex), axis=1)
    # Arg_SC_dt_index.apply(lambda x: Get_Vol_Area_shp(x.index, x.loc_sdat_file, x.ts_index), axis=1)
    # np.vectorize(Get_Vol_Area_shp)(Arg_SC_dt_index, temp_out_clp_sdat_file, ts_name_GivenIndex)          # Arg_SC_dt_index.apply(Get_Vol_Area_shp, axis=1)
    # np.vectorize(Get_Vol_Area_shp)(Arg_SC_dt_index, out_clip_sdat)          # (Arg_SC_dt_index)      # (Arg_SC_dt_index, out_clip_sdat)


# %% READING TIMESTAMP NAMES FROM CSV FILE
# reading timestamp (ts) names from a file to assign them to new file names

loc_ts_folder = 'C:/Users/13004522/Downloads/SharedFiles_ProfJames/Testing_Files/out/'
loc_ts_csv_file = '{}SHP_Filename.csv'.format(loc_ts_folder)
ts_name = pd.read_csv(loc_ts_csv_file)


# %% READING SUBCATCHMENTS NAMES FROM CSV FILE
# reading subcatchment (sc) names from a file to assign them to new file names

loc_sc_folder = 'C:/Users/13004522/Downloads/SharedFiles_ProfJames/Rainfall_Data/modified_from_Siming/SC/'
loc_sc_csv_file = '{}Sub_catchments.csv'.format(loc_sc_folder)
sc_name = pd.read_csv(loc_sc_csv_file)


# %% OUTPUT FOLDER
# Folder where all the results will be stored
out_folder = 'C:/Users/13004522/Downloads/SharedFiles_ProfJames/Testing_Files/out2/'


# %% DECLARING ARGUMENTS FOR TIMESTAMPS
# the number of rows or total number of point shafiles

Arg_TS_dt_index = pd.DataFrame()
Arg_TS_dt_index['ts_index'] = pd.Series(range(ts_name.shape[0]))
# Arg_TS_dt_index = np.arange(ts_name.shape[0])


# %% DECLARING ARGUMENTS FOR SUBCATCHMENTS
# the number of rows or total number of subcatchments

Arg_SC_dt_index = pd.DataFrame()
Arg_SC_dt_index['sc_index'] = pd.Series(range(sc_name.shape[0]))
# Arg_SC_dt_index = np.arange(sc_name.shape[0])


# %% RUNNING THE FUNCTION Get_Simplified_Raster

Arg_TS_dt_index.apply(lambda x: Get_Simplified_Raster(x.ts_index, Arg_SC_dt_index), axis=1)
# arg1: each row index in dataframe Arg_TS_dt_index; it is a dataframe
# arg2: all dataframe indexes in Arg_SC_dt_index; it is a dataframe

# np.vectorize(Get_Simplified_Raster)(Arg_TS_dt_index)


# %% ENDING TIME

ending_time = time.time()
print('Done! in {}'.format(ending_time - starting_time))
