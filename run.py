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

ax1 = plt.subplot2grid((10,1), (0,0), rowspan = 4, colspan = 1)
ax2 = plt.subplot2grid((10,1), (5,0), rowspan = 4, colspan = 1)
ax1.plot(ibm['close'], linewidth = 2.5)
ax1.set_title('IBM CLOSE PRICE')
ax2.plot(ibm['rsi_14'], color = 'orange', linewidth = 2.5)
ax2.axhline(30, linestyle = '--', linewidth = 1.5, color = 'grey')
ax2.axhline(70, linestyle = '--', linewidth = 1.5, color = 'grey')
ax2.set_title('IBM RELATIVE STRENGTH INDEX')
plt.show()

# First, we are defining a function named ‘implement_rsi_strategy’ which takes the stock prices (‘prices’), and the RSI values (‘rsi’) as parameters.
# Inside the function, we are creating three empty lists (buy_price, sell_price, and rsi_signal) in which the values will be appended while creating 
# the trading strategy. After that, we are implementing the trading strategy through a for-loop. Inside the for-loop, we are passing certain conditions, 
# and if the conditions are satisfied, the respective values will be appended to the empty lists. If the condition to buy the stock gets satisfied, the 
# buying price will be appended to the ‘buy_price’ list, and the signal value will be appended as 1 representing to buy the stock. Similarly, if the 
# condition to sell the stock gets satisfied, the selling price will be appended to the ‘sell_price’ list, and the signal value will be appended as -1 
# representing to sell the stock. Finally, we are returning the lists appended with values. Then, we are calling the created function and stored the values 
# into their respective variables. The list doesn’t make any sense unless we plot the values. So, let’s plot the values of the created trading lists.

def implement_rsi_strategy(prices, rsi):    
    buy_price = []
    sell_price = []
    rsi_signal = []
    signal = 0

    for i in range(len(rsi)):
        if rsi[i-1] > 30 and rsi[i] < 30:
            if signal != 1:
                buy_price.append(prices[i])
                sell_price.append(np.nan)
                signal = 1
                rsi_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                rsi_signal.append(0)
        elif rsi[i-1] < 70 and rsi[i] > 70:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(prices[i])
                signal = -1
                rsi_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                rsi_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            rsi_signal.append(0)
            
    return buy_price, sell_price, rsi_signal
            

buy_price, sell_price, rsi_signal = implement_rsi_strategy(ibm['close'], ibm['rsi_14'])

# We are plotting the Relative Strenght Index values along with the buy and sell signals generated by the trading strategy. We can 
# observe that whenever the RSI line crosses from above to below the lower band or the oversold level, a green-colored buy signal 
# is plotted in the chart. Similarly, the RSI line crosses from below to above the upper band or the overbought level, a red-colored 
# sell signal is plotted in the chart.

ax1 = plt.subplot2grid((10,1), (0,0), rowspan = 4, colspan = 1)
ax2 = plt.subplot2grid((10,1), (5,0), rowspan = 4, colspan = 1)
ax1.plot(ibm['close'], linewidth = 2.5, color = 'skyblue', label = 'IBM')
ax1.plot(ibm.index, buy_price, marker = '^', markersize = 10, color = 'green', label = 'BUY SIGNAL')
ax1.plot(ibm.index, sell_price, marker = 'v', markersize = 10, color = 'r', label = 'SELL SIGNAL')
ax1.set_title('IBM RSI TRADE SIGNALS')
ax2.plot(ibm['rsi_14'], color = 'orange', linewidth = 2.5)
ax2.axhline(30, linestyle = '--', linewidth = 1.5, color = 'grey')
ax2.axhline(70, linestyle = '--', linewidth = 1.5, color = 'grey')
plt.show()