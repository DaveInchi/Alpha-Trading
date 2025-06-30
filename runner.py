import json
import requests
from utils.atr_calc import calc_atr
from utils.hystory_data_loader import get_hystory_data
from trading import *

S1_DAYS = 55

def turtle_check(stock_data, day_period):
    """Executes the turtle trading strategy over the given stock data."""
    in_position_long = False
    in_position_short = False
    switch = 0

    for i in range(day_period - 1, len(stock_data)):
        window_data = stock_data[switch:i + 1]

        if not in_position_short:
            in_position_long = entry_long_check(window_data, day_period)
            if in_position_long:
                if not scaling_long(window_data, day_period):
                    in_position_long = exit_long_check(window_data, day_period)

        if not in_position_long:
            in_position_short = entry_short_check(window_data, day_period)
            if in_position_short:
                if not scaling_short(window_data, day_period):
                    in_position_short = exit_short_check(window_data, day_period)

        switch += 1

    print("\n\n" + "-" * 30)
    print(f"Total PNL: {pass_total_pnl()}")
    print("-" * 30)

if __name__ == "__main__":
    stock_data = get_hystory_data('SPY', 2)[::-1]
    turtle_check(stock_data, S1_DAYS)