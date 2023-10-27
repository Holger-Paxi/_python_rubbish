import pandas as pd
import numpy as np

def create_csv(name: str, dim: int) -> None:
    df = pd.DataFrame(np.arange(dim), columns=[name])
    df.to_csv(name + '.csv')


if __name__ == '__main__':
    create_csv('df1', 1000)
    create_csv('df2', 300)
