def clean_q_data(dataframe):
    '''
    input: dataframe with re-named columns
    output: dataframe, series, series
    '''
    import numpy as np
    import pandas as pd
    # datetime operations
    dataframe['dt'] = pd.to_datetime(dataframe['dt_string'])
    dataframe['year'] = dataframe['dt'].dt.year
    dataframe['month'] = dataframe['dt'].dt.month
    dataframe['day'] = dataframe['dt'].dt.day

    # new datetime without time
    dataframe['timestamp'] = pd.to_datetime(dataframe[['year','month', 'day']], errors='coerce')

    # make series from groupby, this has timestamp as index
    daily_q = dataframe.groupby(['timestamp'])['cfs'].mean()

    # make df from series
    daily_dataframe = pd.DataFrame(daily_q)

    # annual peak Q
    #annual_peak_q = dataframe.groupby(dataframe.year)['cfs'].max()

    return(daily_dataframe)
