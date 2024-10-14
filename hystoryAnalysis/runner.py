import json
import requests

from utils.atr_calc import calc_atr
from utils.hystory_data_loader import get_hystory_data
from trading import *

long_entry_counter = 0
short_entry_counter = 0

def turtle_check(stock_data, day_period):
    global long_entry_counter, short_entry_counter

    for i in range(len(stock_data) - day_period, 0, -1):
        print(stock_data[i]['close'])



stockdata = get_hystory_data('SPY', 2)
turtle_check(stockdata, 20)

