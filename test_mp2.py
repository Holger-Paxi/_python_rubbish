import pandas as pd
import numpy as np
import multiprocessing as mp
import timeit, sys

df = pd.read_csv('./foo.csv')
df['start-digits'] = None

startTime = timeit.default_timer()

def card_handler(x):
    x['start-digits'] = x['Card Number']. apply(strip_digits)
    return x

def strip_digits(x):
    return str(x)[:4]

def parallelise(dataframe, func):
    dataframe_split = np.array_split(dataframe, partitions)
    pool = mp.Pool(cores)
    dataframe_return = pd.concat(pool.map(func, dataframe_split), ignore_index=True)
    pool.close()

    return dataframe_return

if __name__ == '__main__':
    mp.set_start_method('spawn') # comment it if it is linux

    cores = mp.cpu_count()
    partitions = cores*10

    df = parallelise(df, card_handler)

    group_dataframe = df.groupby(['start-digits'])
    size_of_group = group_dataframe.size()

    print(size_of_group)
    print(group_dataframe.get_group('6011'))

    stopTime = timeit.default_timer() - startTime
    round_time = round(stopTime, 6)

    print(round_time, 'sec handle time set on 1.5mil rows')

    print('cpu_threads', cores)
    print('split size', partitions)