import json
import requests
from utils.atr_calc import calc_atr
from utils.hystory_data_loader import get_hystory_data
from utils.pnl_calc import calc_pnl

in_position_long = False
in_position_short = False
long_stop_loss_price = 0
long_implied_stop_price = 0
short_stop_loss_price = 0
short_implied_stop_price = 0

risk_value = 1000
comission = 0
num_of_shares = 0

entry_prices_avg = 0
total_pnl = 0
total_realized_pnl = 0
total_unrealized_pnl = 0

last_ent_p = 0
scaling_long_atr = 0
scaling_short_atr = 0
counter = 0

# Returns the highest closing price within the specified day period.
def get_highest_price(stock_data, day_period):
    highest_price = 0
    for i in range(0, day_period - 1):
        if(stock_data[i]['close'] > highest_price):
            highest_price = stock_data[i]['close']
    return highest_price


# Returns the lowest closing price within the specified day period.
def get_lowest_price(stock_data, day_period):
    lowest_price = 1000000
    for i in range(0, day_period - 1):
        if(stock_data[i]['close'] < lowest_price):
            lowest_price = stock_data[i]['close']
    return lowest_price



# Sets the stop loss for long positions based on ATR and current closing price.
def set_stop_loss_long(stock_data, day_period):
    atr = calc_atr(stock_data, day_period)
    stop_loss_price = round(stock_data[-1]['close'] - (atr * 2), 2)
    return stop_loss_price


# Sets the stop loss for short positions based on ATR and current closing price.
def set_stop_loss_short(stock_data, day_period):
    atr = calc_atr(stock_data, day_period)
    stop_loss_price = round(stock_data[-1]['close'] + (atr * 2), 2)
    return stop_loss_price

# Sets the implied stop for long position based on ATR and current closing price.
def set_implied_stop_long(stock_data, day_period):
    array = []
    for i in range(0, (day_period - 1)):
        array.append(stock_data[i]['close'])
    array = array[int(len(array) / 2):]
    return min(array)


# Sets the implied stop for short position based on ATR and current closing price.
def set_implied_stop_short(stock_data, day_period):
    array = []
    for i in range(0, (day_period - 1)):
        array.append(stock_data[i]['close'])
    array = array[int(len(array) / 2):]
    return max(array)



def entry_long_check(stock_data, day_period):
    global in_position_long, long_stop_loss_price, long_implied_stop_price, last_ent_p, scaling_long_atr, entry_prices_avg, total_unrealized_pnl, num_of_shares, counter

    highest_price = get_highest_price(stock_data, day_period - 1)
    
    if(counter == 0):
        if(stock_data[-1]['close'] >= highest_price):
            in_position_long = True
            last_ent_p = stock_data[-1]['close']
            counter += 1

            atr = calc_atr(stock_data, day_period)
            scaling_long_atr = atr
            num_of_shares += int((risk_value - comission) / (2 * atr))

            entry_prices_avg = stock_data[-1]['close']
            total_unrealized_pnl = round((stock_data[-1]['close'] - entry_prices_avg) * num_of_shares)

            long_stop_loss_price = set_stop_loss_long(stock_data, day_period)
            long_implied_stop_price = set_implied_stop_long(stock_data, day_period)

            print("Today's close price: " + str(stock_data[-1]['close']) + "  Today's date: " + stock_data[-1]['date'][0:10] + "  In position long: " + str(in_position_long) + "  This is the first long entry!")
            #print("Highest price: " + str(highest_price))
            print("Stop loss: " + str(long_stop_loss_price) + " Implied Stop: " + str(long_implied_stop_price))
            print("My unrealized pnl: " + str(total_unrealized_pnl))
            print("Counter: " + str(counter))
            print("Shares in this position: " + str(num_of_shares))
            print("I am in this sh!t for long!!!!")
            print("------------------------------")
    

    return in_position_long


def entry_short_check(stock_data, day_period):
    global in_position_short, short_stop_loss_price, short_implied_stop_price, last_ent_p, scaling_short_atr, entry_prices_avg, total_unrealized_pnl, num_of_shares, counter
    lowest_price = get_lowest_price(stock_data, day_period)

    costs = 0
    if(counter == 0):
        if(stock_data[-1]['close'] <= lowest_price):
            in_position_short = True
            last_ent_p = stock_data[-1]['close']
            counter += 1

            atr = calc_atr(stock_data, day_period)
            scaling_short_atr = atr 
            num_of_shares += int((risk_value - comission) / (2 * atr))

            entry_prices_avg = stock_data[-1]['close']
            total_unrealized_pnl = round((stock_data[-1]['close'] - entry_prices_avg) * num_of_shares)
            
            short_stop_loss_price = set_stop_loss_short(stock_data, day_period)
            short_implied_stop_price = set_implied_stop_short(stock_data, day_period)

            print("Today's close price: " + str(stock_data[-1]['close']) + "  Today's date: " + stock_data[-1]['date'][0:10] + " In position short: " + str(in_position_short) + "  This is the first short entry!")
            #print("Lowest price: " + str(lowest_price))
            print("Stop loss: " + str(short_stop_loss_price) + " Implied Stop: " + str(short_implied_stop_price))
            print("My unrealized pnl: " + str(total_unrealized_pnl))
            print("Counter: " + str(counter))
            print("Shares in this position: " + str(num_of_shares))
            print("Short hoes never a problem!!!!")
            print("------------------------------")

    return in_position_short




def exit_long_check(stock_data, day_period):
    global in_position_long, long_stop_loss_price, long_implied_stop_price, last_ent_p, scaling_long_atr, total_realized_pnl, entry_prices_avg, num_of_shares, counter
    long_implied_stop_price = set_implied_stop_long(stock_data, day_period)
    if(stock_data[-1]['close'] < long_stop_loss_price):
        in_position_long = False
        total_realized_pnl = round(total_realized_pnl + (stock_data[-1]['close'] - entry_prices_avg/counter) * num_of_shares, 2)
        counter = 0
        print("Today's close price: " + str(stock_data[-1]['close']) + "  Today's date: " + stock_data[-1]['date'][0:10] + " In position: " + str(in_position_long))
        print("Stop loss hit: " + str(long_stop_loss_price))
        print("Go out while you can, exited long trade!)")
        print("My realized pnl: " + str(round(total_realized_pnl, 2)))
        print("Counter: " + str(counter))
        print("------------------------------")
        num_of_shares = 0
        long_stop_loss_price = 0
        last_ent_p = 0
        scaling_long_atr = 0
        entry_prices_avg = 0


    elif(stock_data[-1]['close'] < long_implied_stop_price):
        in_position_long = False
        total_realized_pnl = round(total_realized_pnl + (stock_data[-1]['close'] - entry_prices_avg/counter) * num_of_shares, 2)
        counter = 0
        print("Today's close price: " + str(stock_data[-1]['close']) + "  Today's date: " + stock_data[-1]['date'][0:10] + " In position: " + str(in_position_long))
        print("Implied stop hit: " + str(long_implied_stop_price))
        print("Go out while you can, exited long trade!)")
        print("My realized pnl: " + str(total_realized_pnl))
        print("Counter: " + str(counter))
        print("------------------------------")
        num_of_shares = 0
        long_implied_stop_price = 0
        last_ent_p = 0
        scaling_long_atr = 0
        entry_prices_avg = 0


    return in_position_long




def exit_short_check(stock_data, day_period):
    global in_position_short, short_stop_loss_price, short_implied_stop_price, last_ent_p, scaling_short_atr, total_realized_pnl, entry_prices_avg, num_of_shares, counter 
    short_implied_stop_price = set_implied_stop_short(stock_data, day_period)
    if(stock_data[-1]['close'] > short_stop_loss_price):
        in_position_short = False
        total_realized_pnl = round(total_realized_pnl + (entry_prices_avg/counter - stock_data[-1]['close']) * num_of_shares, 2)
        counter = 0
        print("Today's close price: " + str(stock_data[-1]['close']) + "  Today's date: " + stock_data[-1]['date'][0:10] + " In position: " + str(in_position_short))
        print("Stop loss hit: " + str(short_stop_loss_price))
        print("Go out while you can, exited short trade!)")
        print("My realized pnl: " + str(total_realized_pnl))
        print("Counter: " + str(counter))
        print("------------------------------")
        num_of_shares = 0
        short_stop_loss_price = 0
        last_ent_p = 0
        scaling_short_atr = 0
        entry_prices_avg = 0

    elif(stock_data[-1]['close'] > short_implied_stop_price):
        in_position_short = False
        total_realized_pnl = round(total_realized_pnl + (entry_prices_avg/counter - stock_data[-1]['close']) * num_of_shares, 2)
        counter = 0
        print("Today's close price: " + str(stock_data[-1]['close']) + "  Today's date: " + stock_data[-1]['date'][0:10] + " In position: " + str(in_position_short))
        print("Implied stop hit: " + str(short_implied_stop_price))
        print("Go out while you can, exited long trade!)")
        print("My realized pnl: " + str(total_realized_pnl))
        print("Counter: " + str(counter))
        print("------------------------------")
        num_of_shares = 0
        short_implied_stop_price = 0
        last_ent_p = 0
        scaling_short_atr = 0
        entry_prices_avg = 0


    return in_position_short

    
def scaling_long(stock_data, day_period):
    global long_stop_loss_price, long_implied_stop_price, last_ent_p, scaling_long_atr, total_realized_pnl, entry_prices_avg, total_unrealized_pnl, num_of_shares, counter 

    scaling_long = False
    num_of_shares_scaling_long = 0
    if(counter != 0 and counter < 4):
        if(stock_data[-1]['close'] >= (last_ent_p + scaling_long_atr / 2)):
            scaling_long = True
            atr = calc_atr(stock_data, day_period)
            num_of_shares_scaling_long += int((risk_value - comission) / (2 * atr))
            num_of_shares += num_of_shares_scaling_long
            counter += 1
            entry_prices_avg += stock_data[-1]['close']
            total_unrealized_pnl = round(stock_data[-1]['close'] - entry_prices_avg / counter) * num_of_shares

            long_stop_loss_price = set_stop_loss_long(stock_data, day_period)
            long_implied_stop_price = set_implied_stop_long(stock_data, day_period)

            print("Today's close price: " + str(stock_data[-1]['close']) + "  Today's date: " + stock_data[-1]['date'][0:10] + "  In position: " + str(in_position_long) + "  Scaling long: " + str(scaling_long))
            print("The price for scaling was: " + str(round(last_ent_p + scaling_long_atr / 2, 2)))
            print("Stop loss: " + str(long_stop_loss_price) + " Implied Stop: " + str(long_implied_stop_price))
            print("My unrealized pnl: " + str(total_unrealized_pnl))
            print("Counter: " + str(counter))
            #print("I am in this sh!t for long!!!!")
            print("Scaling long is working bitches!!!!")
            print("Shares in this position: " + str(num_of_shares))
            print("------------------------------")
            last_ent_p = stock_data[-1]['close']
            scaling_long_atr = atr
    
    return scaling_long
    

    
    
def scaling_short(stock_data, day_period):
    global short_stop_loss_price, short_implied_stop_price, last_ent_p, scaling_short_atr, total_realized_pnl, entry_prices_avg,total_unrealized_pnl, num_of_shares, counter

    scaling_short = False
    num_of_shares_scaling_short = 0
    if(counter != 0 and counter < 4):
        if(stock_data[-1]['close'] <= (last_ent_p - scaling_short_atr / 2)):
            scaling_short = True
            atr = calc_atr(stock_data, day_period)
            num_of_shares_scaling_short += int((risk_value - comission) / (2 * atr))
            num_of_shares += num_of_shares_scaling_short
            counter += 1
            entry_prices_avg += stock_data[-1]['close']
            total_unrealized_pnl = round(entry_prices_avg / counter - stock_data[-1]['close']) * num_of_shares

            short_stop_loss_price = set_stop_loss_short(stock_data, day_period)
            short_implied_stop_price = set_implied_stop_short(stock_data, day_period)

            print("Today's close price: " + str(stock_data[-1]['close']) + "  Today's date: " + stock_data[-1]['date'][0:10] + "  In position: " + str(in_position_short) + "  Scaling short: " + str(scaling_short))
            print("The price for scaling was: " + str(round(last_ent_p - scaling_short_atr / 2)))
            print("Stop loss: " + str(short_stop_loss_price) + " Implied Stop: " + str(short_implied_stop_price))
            print("My unrealized pnl: " + str(total_unrealized_pnl))
            print("Counter: " + str(counter))
            #print("I am in this sh!t for long!!!!")
            print("Shares in this position: " + str(num_of_shares))
            print("Scaling short is working bitches!!!!")
            print("------------------------------")
            last_ent_p = stock_data[-1]['close']
            scaling_short_atr = atr
    
    return scaling_short
    

def pass_total_pnl():
    global total_pnl
    total_pnl = total_realized_pnl + total_unrealized_pnl
    return total_pnl



#stockdata = get_hystory_data('SPY', 2)
#entry_long_check(stockdata, s1_period)
