import json
import requests

from utils.atr_calc import calc_atr
from utils.hystory_data_loader import get_hystory_data
from trading import *

stop_loss = 0
implied_stop_price = 0
s1_days = 20
capital = 500000
num_of_shares = 0
r_perc = 0.02



def turtle_check(stock_data, day_period):
    global stop_loss, implied_stop_price, capital, num_of_shares

    in_position_long = False
    in_position_short = False
    switch = 0

    for i in range(day_period - 1, len(stock_data)):
        entry_long_check_params = entry_long_check(stock_data[switch:i], day_period, capital, num_of_shares, r_perc)
        in_position_long = entry_long_check_params[0]
        stop_loss = entry_long_check_params[1]
        implied_stop_price = entry_long_check_params[2]
        capital = entry_long_check_params[3]
        num_of_shares = entry_long_check_params[4]


        if(in_position_long == True):
            exit_long_check_params = exit_long_check(stock_data[switch:i], capital, num_of_shares)
            in_position_long = exit_long_check_params[0]
            stop_loss = exit_long_check_params[1]
            implied_stop_price = exit_long_check_params[2]
            capital = exit_long_check_params[3]
            num_of_shares = exit_long_check_params[4]
        
        
        switch += 1

        
        



stockdata = get_hystory_data('SPY', 1)
reversed_stockdata = stockdata[::-1]
turtle_check(reversed_stockdata, 20)

