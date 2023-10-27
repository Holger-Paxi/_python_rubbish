#%% tools
import pandas as pd
import os
from csv import DictWriter

#%% Reading inputs from text file
input = pd.read_table('input_table.txt', header=None)
input.columns = ['initial', 'final']

#%% FUNCTION 2
def function_2_sc(
    arg_sc_name_df_pre_vosc_dbf,
    arg_ts_name_df_suf_vosc_dbf,
    arg_ts_name_df_timestamp,
    arg_sc_name_df_subcatchment,
    arg_ts_name_df_id_ts
    ):

    path = arg_sc_name_df_pre_vosc_dbf + arg_ts_name_df_suf_vosc_dbf
    isFile = os.path.isfile(path)

    if isFile:
        pass
    else:
        field_names = ['ID', 'SC', 'TS', 'PATH', 'ISFILE']
        first_feature_record = {
            'ID': arg_ts_name_df_id_ts,
            'SC': arg_sc_name_df_subcatchment,
            'TS': arg_ts_name_df_timestamp,
            'PATH': path,
            'ISFILE': isFile}

        with open('path_exist.csv', 'a+', newline='') as csv_file:
            record_writer = DictWriter(csv_file, fieldnames=field_names)
            record_writer.writerow(first_feature_record)

#%% FUNCTION 1
def function_1_ts(
    arg_sc_name_df,
    arg_ts_name_df_suf_vosc_dbf,
    arg_ts_name_df_timestamp,
    arg_ts_name_df_id_ts
    ):

    # EXECUTE FUNCTION 2
    arg_sc_name_df.apply(lambda arg: function_2_sc(
        arg.pre_vosc_dbf,
        arg_ts_name_df_suf_vosc_dbf,
        arg_ts_name_df_timestamp,
        arg.subcatchment,
        arg_ts_name_df_id_ts
        ),
        axis=1)

#%% FUNCTION 0
def function_0(
    initial_index, 
    final_index
    ):

    #%% Machine
    # container = 'sing20'
    container = '_SP_m_test'

    # #%% SET NUMBER OF ITERATIONS
    # # remember: the first one is inclusive, whereas the last one is exclusive
    # initial_index = 122201
    # final_index =   122501

    #%% INPUT AND OUTPUT FOLDER
    root_child_directory = 'C:/Users/HOLGER/Downloads/SharedFiles_ProfJames/_Spline_Surface/_global/'
    root_parent_directory = 'C:/Users/HOLGER/Downloads/SharedFiles_ProfJames/_Spline_Surface/'

    #%% INPUT TIMESTAMPS (ts) THROUGH CSV FILES
    # IMPORTANT: the csv file must have a title and be limited to one column
    ts_csv_filename = '_SHP_Filename.csv'
    location_ts_csv_folder = root_child_directory
    location_ts_csv_file = location_ts_csv_folder + ts_csv_filename
    ts_name_df = pd.read_csv(location_ts_csv_file)

    #%% INPUT SUBCATCHMENTS (sc) THROUGH CSV FILE
    sc_csv_filename = '_CSV_subcatchment.csv'
    location_sc_csv_folder = root_child_directory
    location_sc_csv_file = location_sc_csv_folder + sc_csv_filename
    sc_name_df = pd.read_csv(location_sc_csv_file)

    #%% INPUT AND OUTPUT FOLDER
    vosc_dbf_results_folder = root_parent_directory + container + '/vosc_dbf' + '_' + str(initial_index) + '_' + str(final_index) + '/'

    #%% DATAFRAME FOR ITERATIONS
    ts_name_df = ts_name_df.iloc[initial_index, :] if initial_index == final_index else ts_name_df.iloc[initial_index: final_index, :]
    ts_name_df = ts_name_df if type(ts_name_df) == type(pd.DataFrame()) else ts_name_df.to_frame().T

    # sufix
    ts_name_df['suf_vosc_dbf'] = '_'+ ts_name_df.timestamp.str[3:] + '.dbf'

    #%% SET SUBCATCHMENT DATAFRAME
    # prefix
    sc_name_df['pre_vosc_dbf'] = vosc_dbf_results_folder + 'vosc_' + sc_name_df.subcatchment.str[3:]

    #%% EXECUTE FUNCTION 1
    ts_name_df.apply(lambda arg: function_1_ts(
        sc_name_df,
        arg.suf_vosc_dbf,
        arg.timestamp,
        arg.id_ts
        ),
        axis=1)
    
    print('done: vosc_dbf_{}_{}'.format(initial_index, final_index))

#%% EXECUTE FUNCTION 0
input.apply(lambda arg: function_0(
    arg.initial,
    arg.final
    ),
    axis=1)

print('totally done')