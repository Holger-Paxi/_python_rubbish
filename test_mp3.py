# %%
import pandas as pd
import numpy as np
import dask.dataframe as dd
from csv import DictWriter
import datetime as dt

# %%
def main_func():
    arg1, arg2 = 1, 10_000
    arg3 = arg2 - arg1 + 1

    arg4, arg5 = 1, 1_000
    arg6 = arg5 - arg4 + 1

    df1 = dataframe1(arg1, arg2, arg3)
    df2 = dataframe2(arg4, arg5, arg6)

    # starting_time = dt.datetime.now()

    # df1.apply(lambda arg: pass_df1(
    #     arg.name, 
    #     arg.a, 
    #     df2
    #     ), axis=1)

    # ending_time = dt.datetime.now()
    # total_time = ending_time - starting_time
    # print('total time {}'.format(total_time))

    starting_time = dt.datetime.now()

    ddata = dd.from_pandas(data=df1, chunksize=100)#, npartitions=100)
    ddata.map_partitions(lambda df: df.apply((lambda arg: pass_df1(arg.name, arg.a, df2)), axis=1)).compute(scheduler='processes')

    ending_time = dt.datetime.now()
    total_time = ending_time - starting_time
    print('total time {}'.format(total_time))

# %%
def pass_df1(arg_df1_name, arg_df1_a, arg_df2):
    arg_df2.apply(lambda arg: pass_df2(
        arg.name, 
        arg.b, 
        arg_df1_name, 
        arg_df1_a
        ), axis=1)

# %%
def pass_df2(
        arg_df2_name, 
        arg_df2_b, 
        arg_df1_name, 
        arg_df1_a
        ):
    addi = addition(arg_df1_a, arg_df2_b)
    subt = subtraction(arg_df1_a, arg_df2_b)
    mult = multiplication(arg_df1_a, arg_df2_b)
    divi = division(arg_df1_a, arg_df2_b)

    write_output(arg_df1_name, arg_df2_name, arg_df1_a, arg_df2_b, addi, subt, mult, divi)

# %%
def write_output(
        arg_df1_name,
        arg_df2_name,
        arg_df1_a,
        arg_df2_b,
        arg_add, 
        arg_sub, 
        arg_mul, 
        arg_div    
    ):
    keys_data = [
        'index_df1',
        'index_df2',
        'df1',
        'df2',
        'addition',
        'subtraction',
        'multiplication',
        'division'
        ]
    dict_data = {
        'index_df1':arg_df1_name,
        'index_df2':arg_df2_name,
        'df1':arg_df1_a,
        'df2':arg_df2_b,
        'addition':arg_add,
        'subtraction':arg_sub,
        'multiplication':arg_mul,
        'division':arg_div
        }
    with open('./test_mp3.csv', 'a+', newline='') as csv_file:
        data_writer = DictWriter(csv_file, fieldnames=keys_data)
        data_writer.writerow(dict_data)

# %%
def dataframe1(arg1, arg2, arg3):
    df1 = np.reshape(np.linspace(start=arg1, stop=arg2, num=arg3), (arg3,1))
    df1 = pd.DataFrame(data=df1, columns=list('a'))
    return df1

# %%
def dataframe2(arg1, arg2, arg3):
    df2 = np.reshape(np.linspace(start=arg1, stop=arg2, num=arg3), (arg3,1))
    df2 = pd.DataFrame(data=df2, columns=list('b'))
    return df2

# %%
def addition(arg1, arg2):
    addi = arg1 + arg2
    return addi

# %%
def subtraction(arg1, arg2):
    subt = arg1 - arg2
    return subt

# %%
def multiplication(arg1, arg2):
    mult = arg1 * arg2
    return mult

# %%
def division(arg1, arg2):
    divi = np.divide(arg1, arg2)
    return divi

# %%
if __name__ == '__main__':
    main_func()

# %%
