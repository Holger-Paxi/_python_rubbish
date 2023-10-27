# %%
import pandas as pd
import numpy as np
import math
import multiprocessing as mp

# %%
depths = pd.read_csv('depths_-33.91_151.191_all_design.csv', skiprows=9)
depths

# %%
stats = pd.read_csv('ECsouth_AllStats.csv')
stats

# %%
increments = pd.read_csv('ECsouth_Increments.csv')
increments

# %%
depths = depths.rename(columns=lambda x: x.strip())
depths

# %%
stats = stats.rename(columns=lambda x: x.strip())
stats

# %%
increments = increments.rename(columns=lambda x: x.strip())
increments

# %%
stats = stats.dropna(axis=0, how='any')
stats

# %%
depths = depths.drop(['Duration'], axis=1)
depths

# %%
depths = depths.rename(columns={'Duration in min': 'Duration'})
depths

# %%
df = pd.merge(depths, increments, on='Duration')
df

# %%
df['Combined'] = df.loc[:, df.columns.str.startswith('Unnamed:')].apply(lambda x: list(x.values), axis=1)
df

# %%
# df['Combined'] = 
df.loc[:, df.columns.str.startswith('Unnamed:')].apply(lambda mylist: [x for x in mylist if math.isnan(x) == False], axis=1)
df

# %%
df['Combined'] = df['Increments'].apply(lambda x: [x]) + df['Combined']
df

# %%
df = df.loc[:, ~df.columns.str.startswith('Unnamed:')]
df

# %%
df.drop(['Increments'], axis=1, inplace=True)
df

# %%
df.rename(columns={'Combined': 'Increments',
          'EventID': 'Event ID'}, inplace=True)
df

# %%
df = pd.merge(df, stats, on='Event ID')
df

# %%
df.columns

# %%
df.shape

# %%
all_prob = ['12EY', '6EY', '4EY', '3EY', '2EY', '63.2%', '50%', '0.5EY',
                  '20%', '0.2EY', '10%', '5%', '2%', '1%', '1 in 200', '1 in 500',
                  '1 in 1000', '1 in 2000']
all_prob

# %%
# prob_filter = ['63.2%', '20%', '10%', '2%', '1%']
prob_filter = ['10%']
prob_filter

# %%
df_inc = pd.DataFrame([pd.Series(x) for x in df.Increments])
df_inc

# %%
df_inc.columns = ['Increments{}'.format(x+1) for x in df_inc.columns]
df_inc

# %%
def rainfall_series(data):
    rows = []
    for prob in prob_filter:
        rainfall = [(i * data[prob])/100 for i in data['Increments']]
        new_row = {'event_id': data['Event ID'], 'duration': data['Duration'], 'excedence_prob': prob,
                   'timestep': data['TimeStep'], 'start_time': data['Burst Start Date'], 'end_time': data['Burst End Date'],
                   'rainfall': rainfall}
        rows.append(new_row)
    return rows

# %%
rainfall_rows = []
for index, row in df.iterrows():
    rainfall_rows = rainfall_rows + rainfall_series(row)

rainfall_rows

# %%
rainfall_df = pd.DataFrame(rainfall_rows, columns=[
                           'event_id', 'duration', 'excedence_prob', 'timestep', 'start_time', 'end_time', 'rainfall'])

rainfall_df

# %%
rainfall_df['start_time'] = pd.to_datetime(
    rainfall_df['start_time'], infer_datetime_format=True)
rainfall_df

# %%
rainfall_df['end_time'] = pd.to_datetime(
    rainfall_df['end_time'], infer_datetime_format=True)
rainfall_df

# %%
rainfall_df.iloc[1:2].iterrows()

# %%
if __name__ == "__main__":
    num_processes = mp.cpu_count()
    print('\nnum_processes:', num_processes)
    # create our pool with `num_processes` processes
    pool = mp.Pool(processes=num_processes-1)
    with mp.Pool() as pool:
         models_output = [item for sublist in 
                          pool.map(run_swmm_model, rainfall_df.iloc[1:2].iterrows(), chunksize=1) 
                          for item in sublist 
                          if item]
        # models_output = pool.map(
        #     run_swmm_model, rainfall_df.iloc[1001:1003].iterrows(), chunksize=1)
        # result_df = pd.DataFrame(chain(*models_output))

# %%
df = pd.DataFrame([[1, 1.5]], columns=['int', 'float'])
df

# %%
row = next(df.iterrows())[1]
# row = df.iterrows()
row
# %%
print(row['int'].dtype)
print(df['int'].dtype)

# %%
models_output = [item 
                for sublist in pool.map(run_swmm_model, rainfall_df.iloc[1:2].iterrows(), chunksize=1) 
                for item in sublist 
                if item]

models_output = []
for sublist in pool.map(run_swmm_model, rainfall_df.iloc[1:2].iterrows(), chunksize=1):
    for item in sublist:
        if item:
            models_output.append(item)

# %%
asd = [_ for ind, _ in pd.DataFrame(data=np.random.rand(4,4),columns=list('abcd')).iterrows()]
asd
# %%
