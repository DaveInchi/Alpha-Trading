import json
import requests
from utils.hystory_data_loader import get_hystory_data

list_atr_dollars = []
s1_days = 20


def calc_tr(stock_data, day):
    high = stock_data[day]['high'] 
    low = stock_data[day]['low']
    close = stock_data[day]['close']

    if(day + 1 <= len(stock_data) - 1):
        N1 = (high / low - 1) * 100
        N2 = abs(close / stock_data[day+1]['low'] - 1) * 100
        N3 = abs(close / stock_data[day+1]['high'] - 1) * 100

        tr = max(max(N1, N2), N3)
        return round(tr, 2)

    else:
        return 0

def calc_atr(stock_data, day_period): 
    tr_sum = 0
    list_tr = []
    for i in range(0, int(day_period)):
            if(i < len(stock_data)):
                tr = calc_tr(stock_data, i)
                list_tr.append(tr)
                tr_sum += tr
            else:
                    break

    atr_perc = round(tr_sum / day_period, 2)
    atr_dollars = round((atr_perc / 100) * stock_data[-1]['close'], 2)
        
    #print(list_atr_dollars)
    return atr_dollars





#stockdata = get_hystory_data('SPY', 1)
#reversed_stockdata = stockdata[::-1]
#calc_atr(reversed_stockdata, s1_days)