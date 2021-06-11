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
print(ibm)