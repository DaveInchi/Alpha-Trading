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



def turtle_check(stock_data, day_period):
    global stop_loss, implied_stop_price, capital, num_of_shares, counter 

    in_position_long = False
    in_position_short = False
    scaling_long_bool = False
    scaling_short_bool = False

    switch = 0

    for i in range(day_period - 1, len(stock_data)):
        if(not in_position_short):
            entry_long_check_params = entry_long_check(stock_data[switch:i], day_period)
            in_position_long = entry_long_check_params[0]
            stop_loss = entry_long_check_params[1]
            implied_stop_price = entry_long_check_params[2]
            num_of_shares = entry_long_check_params[3]



            if(in_position_long):
                scaling_long_params = scaling_long(stock_data[switch:i], day_period)
                scaling_long_bool = scaling_long_params[0]
                stop_loss = scaling_long_params[1]
                implied_stop_price = scaling_long_params[2]
                num_of_shares = scaling_long_params[3]

                if(scaling_long_bool == False):
                    exit_long_check_params = exit_long_check(stock_data[switch:i])
                    in_position_long = exit_long_check_params[0]
                    stop_loss = exit_long_check_params[1]
                    implied_stop_price = exit_long_check_params[2]
                    num_of_shares = exit_long_check_params[3]



        if(not in_position_long):
            entry_short_check_params = entry_short_check(stock_data[switch:i], day_period)
            in_position_short = entry_short_check_params[0]
            stop_loss = entry_short_check_params[1]
            implied_stop_price = entry_short_check_params[2]
            num_of_shares = entry_short_check_params[3]



            if(in_position_short):
                scaling_short_params = scaling_short(stock_data[switch:i], day_period)
                scaling_short_bool = scaling_short_params[0]
                stop_loss = scaling_short_params[1]
                implied_stop_price = scaling_short_params[2]
                num_of_shares = scaling_short_params[3]

                if(scaling_short_bool == False):
                    exit_short_check_params = exit_short_check(stock_data[switch:i])
                    in_position_short = exit_short_check_params[0]
                    stop_loss = exit_short_check_params[1]
                    implied_stop_price = exit_short_check_params[2]
                    num_of_shares = exit_short_check_params[3]


        switch += 1

        

        
        



stockdata = get_hystory_data('SPY', 1)
reversed_stockdata = stockdata[::-1]
turtle_check(reversed_stockdata, 20)

