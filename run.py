import pandas as pd 
import matplotlib.pyplot as plt
import requests
import numpy as np
from math import floor
from termcolor import colored as cl 

plt.style.use('fivethirtyeight')
plt.rcParams['figure.figsize'] = (20, 10)

# The first thing we did is to define a function named ‘get_historical_data’ that takes the stock’s symbol (‘symbol’) as a required parameter 
# and the starting date of the historical data (‘start_date’) as an optional parameter. Inside the function, we are defining the API key 
# and the URL and stored them into their respective variable. Next, we are extracting the historical data in JSON format using the ‘get’ function 
# and stored it into the ‘raw_df’ variable. After doing some processes to clean and format the raw JSON data, we are returning it in the form of 
# a clean Pandas dataframe. Finally, we are calling the created function to pull the historic data of IBM from the starting of 2020 and stored it 
# into the ‘ibm’ variable.

def get_historical_data(symbol, start_date = None):
    api_key = open(r'api_key.txt')
    api_url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&apikey={api_key}&outputsize=full'
    raw_df = requests.get(api_url).json()
    df = pd.DataFrame(raw_df[f'Time Series (Daily)']).T
    df = df.rename(columns = {'1. open': 'open', '2. high': 'high', '3. low': 'low', '4. close': 'close', '5. adjusted close': 'adj close', '6. volume': 'volume'})
    for i in df.columns:
        df[i] = df[i].astype(float)
    df.index = pd.to_datetime(df.index)
    df = df.iloc[::-1].drop(['7. dividend amount', '8. split coefficient'], axis = 1)
    if start_date:
        df = df[df.index >= start_date]
    return df

ibm = get_historical_data('IBM', '2020-01-01')
ibm
print(ibm)

# Firstly, we are defining a function named ‘get_rsi’ that takes the closing price of a stock (‘close’) and the lookback period (‘lookback’) as parameters. 
# Inside the function, we are first calculating the returns of the stock using the ‘diff’ function provided by the Pandas package and stored it into the ‘ret’ 
# variable. This function basically subtracts the current value from the previous value. Next, we are passing a for-loop on the ‘ret’ variable to distinguish 
# gains from losses and append those values to the concerning variable (‘up’ or ‘down’). Then, we are calculating the Exponential Moving Averages for both the 
# ‘up’ and ‘down’ using the ‘ewm’ function provided by the Pandas package and stored them into the ‘up_ewm’ and ‘down_ewm’ variable respectively. Using these 
# calculated EMAs, we are determining the Relative Strength by following the formula we discussed before and stored it into the ‘rs’ variable. By making use of 
# the calculated Relative Strength values, we are calculating the RSI values by following its formula. After doing some data processing and manipulations, we 
# are returning the calculated Relative Strength Index values in the form of a Pandas dataframe. Finally, we are calling the created function to store the RSI 
# values of IBM with 14 as the lookback period.

def get_rsi(close, lookback):
    ret = close.diff()
    up = []
    down = []
    for i in range(len(ret)):
        if ret[i] < 0:
            up.append(0)
            down.append(ret[i])
        else:
            up.append(ret[i])
            down.append(0)
    up_series = pd.Series(up)
    down_series = pd.Series(down).abs()
    up_ewm = up_series.ewm(com = lookback - 1, adjust = False).mean()
    down_ewm = down_series.ewm(com = lookback - 1, adjust = False).mean()
    rs = up_ewm/down_ewm
    rsi = 100 - (100 / (1 + rs))
    rsi_df = pd.DataFrame(rsi).rename(columns = {0:'rsi'}).set_index(close.index)
    rsi_df = rsi_df.dropna()
    return rsi_df[3:]

ibm['rsi_14'] = get_rsi(ibm['close'], 14)
ibm = ibm.dropna()
ibm
print(ibm)