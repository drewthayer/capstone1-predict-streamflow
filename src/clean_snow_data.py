import numpy as np
import pandas as pd
def remove_outliers(df):
    '''
    input: dataframe of snotel data with columns re-named for degrees C
    output: dataframe
    '''
    import pandas as pd
    # clear min airtemp outliers
    df.drop(df[df.airtemp_min_C > 18].index, inplace=True)
    df.drop(df[df.airtemp_min_C < -40].index, inplace=True)
    # clear max airtemp outliers
    df.drop(df[df.airtemp_max_C > 50].index, inplace=True)
    df.drop(df[df.airtemp_max_C < -45].index, inplace=True)
    return(df)

def clean_snow_data(dataframe):
    '''
    requirements: 'remove_outliers' function
    input: dataframe with re-named columns
    output: dataframe
    '''
    snow_df = dataframe
    # unit conversions to metric
    snow_df['swe_start_m'] = snow_df.swe_start_in * 0.0254
    snow_df['airtemp_max_C'] = 5/9*(snow_df.airtemp_max_F - 32)
    snow_df['airtemp_min_C'] = 5/9*(snow_df.airtemp_min_F - 32)
    snow_df['airtemp_mean_C'] = 5/9*(snow_df.airtemp_mean_F - 32)
    snow_df['precip_start_m'] = snow_df.precip_start_in * 0.0254
    snow_df['precip_incr_m'] = snow_df.precip_incr_in * 0.0254

    # drop standard unit columns
    snow_df.drop(['swe_start_in'], axis=1, inplace=True)
    snow_df.drop(['airtemp_max_F'], axis=1, inplace=True)
    snow_df.drop(['airtemp_min_F'], axis=1, inplace=True)
    snow_df.drop(['airtemp_mean_F'], axis=1, inplace=True)
    snow_df.drop(['precip_start_in'], axis=1, inplace=True)
    snow_df.drop(['precip_incr_in'], axis=1, inplace=True)

    # datetime operations
    snow_df['dt'] = pd.to_datetime(snow_df['dt_string'])
    snow_df['year'] = snow_df['dt'].dt.year
    snow_df['month'] = snow_df['dt'].dt.month

    # drop datetime string column
    snow_df.drop(['dt_string'], axis=1, inplace=True)

    # remove 2018 data
    snow_df.drop(snow_df[snow_df.year == 2018].index, inplace=True)

    # remove rows with swe=0
    snow_df.drop(snow_df[snow_df.swe_start_m == 0].index, inplace=True)

    # remove september data (highly volatile and uncharacteristic)
    snow_df.drop(snow_df[snow_df.month == 9].index, inplace=True)

    # remove all data but spring
#     snow_df.drop(snow_df[snow_df.month == 10].index, inplace=True)
#     snow_df.drop(snow_df[snow_df.month == 11].index, inplace=True)
#     snow_df.drop(snow_df[snow_df.month == 12].index, inplace=True)
#     snow_df.drop(snow_df[snow_df.month == 1].index, inplace=True)
#     snow_df.drop(snow_df[snow_df.month == 2].index, inplace=True)
#     snow_df.drop(snow_df[snow_df.month == 3].index, inplace=True)

    #set snow df index to dt
    snow_df.set_index(snow_df.dt, inplace=True)

    # clean airtemp outliers
    snow_df = remove_outliers(snow_df)

    # # annual peak swe
    # annual_peak_swe = snow_df.groupby(snow_df.year)['swe_start_m'].max()
    #
    # # annual cumulative swe
    # cumsum_swe = snow_df.groupby(snow_df['year'])['swe_start_m'].cumsum()
    #
    # # monthly cumulative swe
    # swe_monthly = snow_df.groupby([snow_df['year'], snow_df['month']])['swe_start_m'].cumsum()

    return(snow_df)
