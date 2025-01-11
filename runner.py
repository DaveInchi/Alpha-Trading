import json
import requests

from utils.atr_calc import calc_atr
from utils.hystory_data_loader import get_hystory_data
from trading import *

s1_days = 20



def turtle_check(stock_data, day_period):

    in_position_long = False
    in_position_short = False
    scaling_long_bool = False
    scaling_short_bool = False

    switch = 0

    for i in range(day_period - 1, len(stock_data)):
        if(not in_position_short):
            in_position_long = entry_long_check(stock_data[switch:i + 1], day_period)

            if(in_position_long):
                scaling_long_bool = scaling_long(stock_data[switch:i + 1], day_period)

                if(scaling_long_bool == False):
                    in_position_long = exit_long_check(stock_data[switch:i + 1], day_period)
                    



        if(not in_position_long):
            in_position_short = entry_short_check(stock_data[switch:i + 1], day_period)

            if(in_position_short):
                scaling_short_bool = scaling_short(stock_data[switch:i + 1], day_period)

                if(scaling_short_bool == False):
                    in_position_short = exit_short_check(stock_data[switch:i + 1], day_period)


        switch += 1


    print("")
    print("")
    print("------------------------------")
    print("Total PNL: " + str(pass_total_pnl()))
    print("------------------------------")

        

        
        



stockdata = get_hystory_data('SPY', 30)
reversed_stockdata = stockdata[::-1]
turtle_check(reversed_stockdata, s1_days)

