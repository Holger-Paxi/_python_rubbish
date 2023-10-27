# %%
from numba import jit
import os
import shutil
import multiprocessing as mp
from itertools import chain 
import pandas as pd
import math
import pyswmm
from pyswmm import Simulation, Nodes
import swmmio
from swmmio.utils import modify_model
import datetime
from swmm.toolkit.shared_enum import SubcatchAttribute, NodeAttribute, LinkAttribute, SystemAttribute
from pyswmm import Output
import sys

sys.version


# %% [markdown]
# reading the data from ARR website. 

# %%
depths = pd.read_csv('depths_-33.91_151.191_all_design.csv', skiprows=9)
stats = pd.read_csv('ECsouth_AllStats.csv')
increments = pd.read_csv('ECsouth_Increments.csv')
# remove white space from column names
depths = depths.rename(columns=lambda x: x.strip())
stats = stats.rename(columns=lambda x: x.strip())
increments = increments.rename(columns=lambda x: x.strip())
# remove na from stats
stats = stats.dropna(axis=0, how='any')

depths = depths.drop(['Duration'], axis=1)
depths = depths.rename(columns={'Duration in min': 'Duration'})
depths.head(1)


# %% [markdown]
# # STEP 1: Construct df with required data
# - merge depths and increaments on "Duration"  
# - merge the result with stats on "Event ID" to get dates of burst event 

# %%
# ARR data
# merge depths and stats on duration
df = pd.merge(depths, increments, on='Duration')
df['Combined'] = df.loc[:, df.columns.str.startswith(
    'Unnamed:')].apply(lambda x: list(x.values), axis=1)
df['Combined'] = df.loc[:, df.columns.str.startswith('Unnamed:')].apply(
    lambda mylist: [x for x in mylist if math.isnan(x) == False], axis=1)
df['Combined'] = df['Increments'].apply(lambda x: [x]) + df['Combined']
df = df.loc[:, ~df.columns.str.startswith('Unnamed:')]
df.drop(['Increments'], axis=1, inplace=True)
df.rename(columns={'Combined': 'Increments',
          'EventID': 'Event ID'}, inplace=True)
df = pd.merge(df, stats, on='Event ID')
df.to_csv('combined_tables.csv')


# %%
print(df.columns)
print(df.shape)


# %% [markdown]
# - Keep only the needed AEPs (you can modifiy to add more or less)
# - Convert Increments to rainfall values in the data frame

# %%
all_prob = ['12EY', '6EY', '4EY', '3EY', '2EY', '63.2%', '50%', '0.5EY',
                  '20%', '0.2EY', '10%', '5%', '2%', '1%', '1 in 200', '1 in 500',
                  '1 in 1000', '1 in 2000']
# choose AEP to keep in the model
prob_filter = ['63.2%', '20%', '10%', '2%', '1%']


# increments dataframe
df_inc = pd.DataFrame([pd.Series(x) for x in df.Increments])
df_inc.columns = ['Increments{}'.format(x+1) for x in df_inc.columns]

# convert increments to rainfall
def rainfall_series(data):
    rows = []
    for prob in prob_filter:
        rainfall = [(i * data[prob])/100 for i in data['Increments']]
        new_row = {'event_id': data['Event ID'], 'duration': data['Duration'], 'excedence_prob': prob,
                   'timestep': data['TimeStep'], 'start_time': data['Burst Start Date'], 'end_time': data['Burst End Date'],
                   'rainfall': rainfall}
        rows.append(new_row)
    return rows


#rainfall_df = df.apply(rainfall_series, axis=1)
rainfall_rows = []
for index, row in df.iterrows():
    rainfall_rows = rainfall_rows + rainfall_series(row)

rainfall_df = pd.DataFrame(rainfall_rows, columns=[
                           'event_id', 'duration', 'excedence_prob', 'timestep', 'start_time', 'end_time', 'rainfall'])
# clean dates
rainfall_df['start_time'] = pd.to_datetime(
    rainfall_df['start_time'], infer_datetime_format=True)
rainfall_df['end_time'] = pd.to_datetime(
    rainfall_df['end_time'], infer_datetime_format=True)

# save to csv
rainfall_df.to_csv('rainfall.csv')
rainfall_df.shape


# %% [markdown]
# # STEP3: Generate the SWMM Series 
# 
# 1. add X (12 or 10 according to Holger) timesteps at the start and end of the timeseries 
#  

# %%
def swmm_timeseries(row):
    padded_steps = 12  # used to pad the start and end of the timeseries
    start_time = row.at['start_time']
    end_time = row.at['end_time']
    timestep = row.at['timestep']
    rainfall = row.at['rainfall']
    # timestep as datetime deltatime
    timestep = datetime.timedelta(minutes=int(timestep))
    #print(start_time, end_time)
    date_series = []
    time_series = []
    t = start_time
    while t <= end_time:
        date_series.append(t.strftime('%m-%d-%Y'))
        time_series.append(t.strftime('%H:%M'))
        t = t + timestep

    # add padding elements to end of series
    for i in range(padded_steps):
        date_series.append(t.strftime('%m-%d-%Y'))
        time_series.append(t.strftime('%H:%M'))
        t = t + timestep

    # add padding elements to start of series
    start_time = start_time - (timestep)
    for i in range(padded_steps):
        date_series.insert(0, start_time.strftime('%m/%d/%Y'))
        time_series.insert(0, start_time.strftime('%H:%M'))
        start_time = start_time - (timestep)

    # add padding to rainfall series
    rainfall = [0 for i in range(padded_steps)] + \
        rainfall + [0 for i in range(padded_steps)]

    # repeat string for each date_series element
    name_series = ['RainSeries1' for x in date_series]
    # create dataframe
    swmm_timeseries_df = pd.DataFrame(
        {'Date': date_series, 'Time': time_series, 'Value': rainfall, 'Name': name_series})
    swmm_timeseries_df.set_index(['Name'], inplace=True)
    return swmm_timeseries_df

# if you need strings use this
#zipped = zip(name_series,date_series,time_series,rainfall)
#strings = ['%s\t%s\t%s\t%s' % (name, date, time, rainfall) for name, date, time, rainfall in zipped]

# debug
# swmm_timeseries(rainfall_df.iloc[1002])


# %% [markdown]
# # STEP4: SWMMIO to create inp files 
# - create inp files using swmmio 
# - using the pattrens 

# %%
inp_template = 'SWMM_Template/template.inp'
options_df_template = swmmio.utils.dataframes.dataframe_from_inp(
    'SWMM_Template/template.inp', '[OPTIONS]')

# to debug
#rainfall_event = rainfall_df.iloc[1002]

# for index,rainfall_event in rainfall_df.iloc[1001:1002].iterrows():


def run_swmm_model(rainfall_event):
    rainfall_event = rainfall_event[1]
    # build the name of the file to write with event_id excedence_prob duration timestep
    # cathcment_event_id_AEP_Duration_Timestep
    my_inp_filename = os.path.join('SWMM_Model', 'Alexandra_' + str(rainfall_event['event_id']) + '_' + str(
        rainfall_event['excedence_prob']) + '_' + str(rainfall_event['duration'])[:-2] + '_' + str(rainfall_event['timestep']) + '.inp')

    # make a copy of the template inp file
    shutil.copyfile(inp_template, my_inp_filename)

    # get the options from the rainfall event
    options_df = options_df_template.copy()
    options_df.at['START_DATE'] = rainfall_event['start_time'].strftime(
        '%m/%d/%Y')
    options_df.at['START_TIME'] = rainfall_event['start_time'].strftime(
        '%H:%M:%S')
    options_df.at['REPORT_START_DATE'] = rainfall_event['start_time'].strftime(
        '%m/%d/%Y')
    options_df.at['REPORT_START_TIME'] = rainfall_event['start_time'].strftime(
        '%H:%M:%S')
    options_df.at['END_DATE'] = rainfall_event['end_time'].strftime('%m/%d/%Y')
    options_df.at['END_TIME'] = rainfall_event['end_time'].strftime('%H:%M:%S')
    options_df.at['REPORT_STEP'] = '00:00:01'
    options_df.at['ROUTING_STEP'] = '00:00:01'
    # write the options to the template
    # replace the timeseries in the template
    modify_model.replace_inp_section(
        my_inp_filename, '[TIMESERIES]', swmm_timeseries(rainfall_event))
    modify_model.replace_inp_section(my_inp_filename, '[OPTIONS]', options_df)

    with Simulation(my_inp_filename) as sim:
        flooding = []

        for step in sim:
            # list of boolean that tells if node is flooding
            nodes_flooding = list(
                filter(lambda node: node.flooding > 0, Nodes(sim)))
            if len(nodes_flooding) == 0:
                pass
            else:
                flooding.extend(list(map(lambda node: {'node': node.nodeid, 'datetime': sim.current_time,
                                                       'flooding_rate': node.flooding, 'excedence_prob': rainfall_event['excedence_prob'], 'duration': rainfall_event['duration'],
                                                       'timestep': rainfall_event['timestep'], 'event_id': rainfall_event['event_id']}, nodes_flooding)))
        # done simulating
        if len(flooding) != 0:
            return flooding
        else:
            return None

# appernatly swmm does not support running multiple instance on the same machine (no safe multithreading)
if __name__ == "__main__":
    num_processes = mp.cpu_count()
    print('\nnum_processes:', num_processes)
    # create our pool with `num_processes` processes
    pool = mp.Pool(processes=num_processes-1)
    with mp.Pool() as pool:
         models_output = [item for sublist in pool.map(run_swmm_model, rainfall_df.iloc[1:2].iterrows(), chunksize=1) for item in sublist if item]
        # models_output = pool.map(
        #     run_swmm_model, rainfall_df.iloc[1001:1003].iterrows(), chunksize=1)
        # result_df = pd.DataFrame(chain(*models_output))

    result_df = pd.DataFrame(models_output)
    print(result_df.shape)
    result_df.head(2)
    # name of csv file and datetime 
    csv_filename = 'Alexandra_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.csv'
    csv_path = os.path.join('Results', csv_filename)
    result_df.to_csv(csv_path)
    print('\nDone!')


# regular loop 
# result = []
# for rainfall_event in rainfall_df.iloc[1001:1002].iterrows():
#     # print progress 
#     print(int(rainfall_event[0]/rainfall_df.shape[0]*100).__str__() + '%')
#     models_output = run_swmm_model(rainfall_event)
#     if models_output:
#         result.extend(models_output)
# result_df = pd.DataFrame(result)
# # name of csv file and datetime 
# csv_filename = 'Alexandra_' + datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.csv'
# csv_path = os.path.join('Results', csv_filename)
# result_df.to_csv(csv_path)
# print('\nDone!')


# %%
result_df


# %% [markdown]
# - test performace of chain vs list comprehension

# %%
# x = []
# for idx,row in rainfall_df.iterrows():
#     y = []
#     # 'timestep', 'start_time', 'end_time'
#     # find the number of timesteps between start_time and end_time
#     num_timesteps = (row['end_time'] - row['start_time']).total_seconds()
#     for i in range(int(num_timesteps)):
#             y.append(i)
#     x.append(y)

# len(x)


# %%
# %%timeit -n 1 -r 1 -s 1
# y = pd.DataFrame(chain(x))

# %%
# %%timeit -n 1 -r 1 -s 1
# y = pd.DataFrame([item for sublist in x for item in sublist])

# %%



