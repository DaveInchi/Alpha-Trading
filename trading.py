import json
import requests
from utils.atr_calc import calc_atr
from utils.hystory_data_loader import get_hystory_data
from utils.pnl_calc import calc_pnl

# Constants
atr_scaling_factor = 1.5
entry_count_limit = 4

# Global variables
in_position_long = False
in_position_short = False
long_stop_loss_price = 0
long_implied_stop_price = 0
short_stop_loss_price = 0
short_implied_stop_price = 0
risk_value = 1000
commission = 0
num_of_shares = 0
entry_prices_avg = 0
total_pnl = 0
total_realized_pnl = 0
total_unrealized_pnl = 0
last_entry_price = 0
scaling_long_atr = 0
scaling_short_atr = 0
counter = 0

def get_highest_price(stock_data, day_period):
    """Returns the highest closing price within the specified day period."""
    return max(stock_data[i]['close'] for i in range(day_period - 1))

def get_lowest_price(stock_data, day_period):
    """Returns the lowest closing price within the specified day period."""
    return min(stock_data[i]['close'] for i in range(day_period - 1))

def set_stop_loss_long(stock_data, day_period):
    """Sets the stop loss for long positions based on ATR and current closing price."""
    atr = calc_atr(stock_data, day_period)
    return round(stock_data[-1]['close'] - (atr * 2), 2)

def set_stop_loss_short(stock_data, day_period):
    """Sets the stop loss for short positions based on ATR and current closing price."""
    atr = calc_atr(stock_data, day_period)
    return round(stock_data[-1]['close'] + (atr * 2), 2)

def set_implied_stop_long(stock_data, day_period):
    """Sets the implied stop for long position based on recent closing prices."""
    closes = [stock_data[i]['close'] for i in range(day_period - 1)]
    return min(closes[len(closes) // 2:])

def set_implied_stop_short(stock_data, day_period):
    """Sets the implied stop for short position based on recent closing prices."""
    closes = [stock_data[i]['close'] for i in range(day_period - 1)]
    return max(closes[len(closes) // 2:])

def entry_long_check(stock_data, day_period):
    """Checks conditions for entering a long position."""
    global in_position_long, long_stop_loss_price, long_implied_stop_price, last_entry_price, scaling_long_atr
    global entry_prices_avg, total_unrealized_pnl, num_of_shares, counter

    highest_price = get_highest_price(stock_data, day_period - 1)
    
    if counter == 0 and stock_data[-1]['close'] >= highest_price:
        in_position_long = True
        last_entry_price = stock_data[-1]['close']
        counter += 1

        atr = calc_atr(stock_data, day_period)
        scaling_long_atr = atr
        num_of_shares += int((risk_value - commission) / (2 * atr))
        entry_prices_avg = stock_data[-1]['close']
        total_unrealized_pnl = round((stock_data[-1]['close'] - entry_prices_avg) * num_of_shares)

        long_stop_loss_price = set_stop_loss_long(stock_data, day_period)
        long_implied_stop_price = set_implied_stop_long(stock_data, day_period)

        print(f"Date: {stock_data[-1]['date'][:10]} | Close: {stock_data[-1]['close']} | In Long: {in_position_long}")
        print(f"Stop Loss: {long_stop_loss_price} | Implied Stop: {long_implied_stop_price}")
        print(f"Unrealized PnL: {total_unrealized_pnl} | Shares: {num_of_shares} | Counter: {counter}")
        print("Entered long position!")
        print("-" * 30)

    return in_position_long

def entry_short_check(stock_data, day_period):
    """Checks conditions for entering a short position."""
    global in_position_short, short_stop_loss_price, short_implied_stop_price, last_entry_price, scaling_short_atr
    global entry_prices_avg, total_unrealized_pnl, num_of_shares, counter

    lowest_price = get_lowest_price(stock_data, day_period)
    
    if counter == 0 and stock_data[-1]['close'] <= lowest_price:
        in_position_short = True
        last_entry_price = stock_data[-1]['close']
        counter += 1

        atr = calc_atr(stock_data, day_period)
        scaling_short_atr = atr
        num_of_shares += int((risk_value - commission) / (2 * atr))
        entry_prices_avg = stock_data[-1]['close']
        total_unrealized_pnl = round((stock_data[-1]['close'] - entry_prices_avg) * num_of_shares)
        
        short_stop_loss_price = set_stop_loss_short(stock_data, day_period)
        short_implied_stop_price = set_implied_stop_short(stock_data, day_period)

        print(f"Date: {stock_data[-1]['date'][:10]} | Close: {stock_data[-1]['close']} | In Short: {in_position_short}")
        print(f"Stop Loss: {short_stop_loss_price} | Implied Stop: {short_implied_stop_price}")
        print(f"Unrealized PnL: {total_unrealized_pnl} | Shares: {num_of_shares} | Counter: {counter}")
        print("Entered short position!")
        print("-" * 30)

    return in_position_short

def exit_long_check(stock_data, day_period):
    """Checks conditions for exiting a long position."""
    global in_position_long, long_stop_loss_price, long_implied_stop_price, last_entry_price, scaling_long_atr
    global total_realized_pnl, entry_prices_avg, num_of_shares, counter

    long_implied_stop_price = set_implied_stop_long(stock_data, day_period)
    current_price = stock_data[-1]['close']
    
    if current_price < long_stop_loss_price or current_price < long_implied_stop_price:
        in_position_long = False
        total_realized_pnl = round(total_realized_pnl + (current_price - entry_prices_avg / counter) * num_of_shares, 2)
        counter = 0
        
        print(f"Date: {stock_data[-1]['date'][:10]} | Close: {current_price} | In Long: {in_position_long}")
        print(f"{'Stop Loss' if current_price < long_stop_loss_price else 'Implied Stop'} Hit: {long_stop_loss_price if current_price < long_stop_loss_price else long_implied_stop_price}")
        print(f"Realized PnL: {total_realized_pnl} | Counter: {counter}")
        print("Exited long position!")
        print("-" * 30)

        num_of_shares = 0
        long_stop_loss_price = 0
        long_implied_stop_price = 0
        last_entry_price = 0
        scaling_long_atr = 0
        entry_prices_avg = 0

    return in_position_long

def exit_short_check(stock_data, day_period):
    """Checks conditions for exiting a short position."""
    global in_position_short, short_stop_loss_price, short_implied_stop_price, last_entry_price, scaling_short_atr
    global total_realized_pnl, entry_prices_avg, num_of_shares, counter

    short_implied_stop_price = set_implied_stop_short(stock_data, day_period)
    current_price = stock_data[-1]['close']
    
    if current_price > short_stop_loss_price or current_price > short_implied_stop_price:
        in_position_short = False
        total_realized_pnl = round(total_realized_pnl + (entry_prices_avg / counter - current_price) * num_of_shares, 2)
        counter = 0
        
        print(f"Date: {stock_data[-1]['date'][:10]} | Close: {current_price} | In Short: {in_position_short}")
        print(f"{'Stop Loss' if current_price > short_stop_loss_price else 'Implied Stop'} Hit: {short_stop_loss_price if current_price > short_stop_loss_price else short_implied_stop_price}")
        print(f"Realized PnL: {total_realized_pnl} | Counter: {counter}")
        print("Exited short position!")
        print("-" * 30)

        num_of_shares = 0
        short_stop_loss_price = 0
        short_implied_stop_price = 0
        last_entry_price = 0
        scaling_short_atr = 0
        entry_prices_avg = 0

    return in_position_short

def scaling_long(stock_data, day_period):
    """Handles scaling into a long position."""
    global long_stop_loss_price, long_implied_stop_price, last_entry_price, scaling_long_atr
    global total_unrealized_pnl, entry_prices_avg, num_of_shares, counter

    scaling_long = False
    if 0 < counter < entry_count_limit and stock_data[-1]['close'] >= (last_entry_price + scaling_long_atr * atr_scaling_factor):
        scaling_long = True
        atr = calc_atr(stock_data, day_period)
        num_shares_added = int((risk_value - commission) / (2 * atr))
        num_of_shares += num_shares_added
        counter += 1
        entry_prices_avg += stock_data[-1]['close']
        total_unrealized_pnl = round((stock_data[-1]['close'] - entry_prices_avg / counter) * num_of_shares)

        long_stop_loss_price = set_stop_loss_long(stock_data, day_period)
        long_implied_stop_price = set_implied_stop_long(stock_data, day_period)

        print(f"Date: {stock_data[-1]['date'][:10]} | Close: {stock_data[-1]['close']} | In Long: {in_position_long} | Scaling: {scaling_long}")
        print(f"Scaling Price: {round(last_entry_price + scaling_long_atr / 2, 2)}")
        print(f"Stop Loss: {long_stop_loss_price} | Implied Stop: {long_implied_stop_price}")
        print(f"Unrealized PnL: {total_unrealized_pnl} | Shares: {num_of_shares} | Counter: {counter}")
        print("Scaled long position!")
        print("-" * 30)

        last_entry_price = stock_data[-1]['close']
        scaling_long_atr = atr

    return scaling_long

def scaling_short(stock_data, day_period):
    """Handles scaling into a short position."""
    global short_stop_loss_price, short_implied_stop_price, last_entry_price, scaling_short_atr
    global total_unrealized_pnl, entry_prices_avg, num_of_shares, counter

    scaling_short = False
    if 0 < counter < entry_count_limit and stock_data[-1]['close'] <= (last_entry_price - scaling_short_atr * atr_scaling_factor):
        scaling_short = True
        atr = calc_atr(stock_data, day_period)
        num_shares_added = int((risk_value - commission) / (2 * atr))
        num_of_shares += num_shares_added
        counter += 1
        entry_prices_avg += stock_data[-1]['close']
        total_unrealized_pnl = round((entry_prices_avg / counter - stock_data[-1]['close']) * num_of_shares)

        short_stop_loss_price = set_stop_loss_short(stock_data, day_period)
        short_implied_stop_price = set_implied_stop_short(stock_data, day_period)

        print(f"Date: {stock_data[-1]['date'][:10]} | Close: {stock_data[-1]['close']} | In Short: {in_position_short} | Scaling: {scaling_short}")
        print(f"Scaling Price: {round(last_entry_price - scaling_short_atr / 2, 2)}")
        print(f"Stop Loss: {short_stop_loss_price} | Implied Stop: {short_implied_stop_price}")
        print(f"Unrealized PnL: {total_unrealized_pnl} | Shares: {num_of_shares} | Counter: {counter}")
        print("Scaled short position!")
        print("-" * 30)

        last_entry_price = stock_data[-1]['close']
        scaling_short_atr = atr

    return scaling_short

def pass_total_pnl():
    """Calculates and returns total PnL."""
    global total_pnl
    total_pnl = total_realized_pnl + total_unrealized_pnl
    return total_pnl