import json
import requests
from utils.atr_calc import calc_atr
from utils.hystory_data_loader import get_hystory_data
from utils.pnl_calc import calc_pnl

s1_period = 20
in_position_long = False
in_position_short = False
long_stop_loss_price = 0
long_implied_stop_price = 0
short_stop_loss_price = 0
short_implied_stop_price = 0
comission = 0
num_of_shares = 0
pnl = 0
total_pnl = 0

last_ent_p = 0
scaling_long_atr = 0
scaling_short_atr = 0

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



def entry_long_check(stock_data, day_period, capital, r_perc):
    global in_position_long, long_stop_loss_price, long_implied_stop_price, last_ent_p, scaling_long_atr, pnl, num_of_shares

    highest_price = get_highest_price(stock_data, day_period - 1)
    
    
    if(stock_data[-1]['close'] >= highest_price):
        in_position_long = True
        last_ent_p = stock_data[-1]['close']

        if(capital > 0):
            atr = calc_atr(stock_data, day_period)
            scaling_long_atr = atr
            num_of_shares += int((capital * r_perc - comission) / (2 * atr))
            pnl = calc_pnl(stock_data, last_ent_p, num_of_shares)
            costs = round(num_of_shares * stock_data[-1]['close'], 2)
            capital = round(capital - costs, 2)

        long_stop_loss_price = set_stop_loss_long(stock_data, day_period)
        long_implied_stop_price = set_implied_stop_long(stock_data, day_period)

        print("Today's close price: " + str(stock_data[-1]['close']) + "  Today's date: " + stock_data[-1]['date'][0:10] + "  In position long: " + str(in_position_long) + "  This is the first long entry!")
        #print("Highest price: " + str(highest_price))
        print("Go in and don't look back! Costs: " + str(costs))
        print("Stop loss: " + str(long_stop_loss_price) + " Implied Stop: " + str(long_implied_stop_price))
        print("And this is how much I have left: " + str(capital))
        print("PnL: " + str(pnl))
        print("I am in this sh!t for long!!!!")
        print("------------------------------")
    

    return [in_position_long, long_stop_loss_price, long_implied_stop_price, capital, num_of_shares]


def entry_short_check(stock_data, day_period, capital, r_perc):
    global in_position_short, short_stop_loss_price, short_implied_stop_price, last_ent_p, scaling_short_atr, pnl, num_of_shares

    lowest_price = get_lowest_price(stock_data, day_period)

    costs = 0
    if(stock_data[-1]['close'] <= lowest_price):
        in_position_short = True
        last_ent_p = stock_data[-1]['close']

        if (capital > 0):
            atr = calc_atr(stock_data, day_period)
            scaling_short_atr = atr 
            num_of_shares += int((capital * r_perc - comission) / (2 * atr))
            pnl = calc_pnl(stock_data, last_ent_p, num_of_shares)
            costs = round(num_of_shares * stock_data[-1]['close'], 2)
            capital = round(capital - costs, 2)

        short_stop_loss_price = set_stop_loss_short(stock_data, day_period)
        short_implied_stop_price = set_implied_stop_short(stock_data, day_period)

        print("Today's close price: " + str(stock_data[-1]['close']) + "  Today's date: " + stock_data[-1]['date'][0:10] + " In position short: " + str(in_position_short) + "This is the first short entry!")
        #print("Lowest price: " + str(lowest_price))
        print("Go in and don't look back! Costs: " + str(costs))
        print("Stop loss: " + str(short_stop_loss_price) + " Implied Stop: " + str(short_implied_stop_price))
        print("And this is how much I have left: " + str(capital))
        print("PnL: " + str(pnl))
        print("Short hoes never a problem!!!!")
        print("------------------------------")

    return [in_position_short, short_stop_loss_price, short_implied_stop_price, capital, num_of_shares]




def exit_long_check(stock_data, capital):
    global in_position_long, long_stop_loss_price, long_implied_stop_price, last_ent_p, scaling_long_atr, total_pnl, pnl, num_of_shares

    if(stock_data[-1]['close'] < long_stop_loss_price):
        in_position_long = False
        pnl = calc_pnl(stock_data, last_ent_p, num_of_shares)
        costs = round(num_of_shares * stock_data[-1]['close'], 2)
        capital += round(capital + costs, 2)
        total_pnl += pnl
        print("Today's close price: " + str(stock_data[-1]['close']) + "  Today's date: " + stock_data[-1]['date'][0:10] + " In position: " + str(in_position_long))
        print("Stop loss hit: " + str(long_stop_loss_price))
        print("Go out while you can, exited long trade!)")
        print("PnL: " + str(pnl))
        print("My capital is now: " + str(capital))
        print("------------------------------")
        num_of_shares = 0
        long_stop_loss_price = 0
        last_ent_p = 0
        scaling_long_atr = 0

    elif(stock_data[-1]['close'] < long_implied_stop_price):
        in_position_long = False
        pnl = calc_pnl(stock_data, last_ent_p, num_of_shares)
        costs = round(num_of_shares * stock_data[-1]['close'], 2)
        capital += round(capital + costs, 2)
        total_pnl += pnl
        print("Today's close price: " + str(stock_data[-1]['close']) + "  Today's date: " + stock_data[-1]['date'][0:10] + " In position: " + str(in_position_long))
        print("Implied stop hit: " + str(long_implied_stop_price))
        print("Go out while you can, exited long trade!)")
        print("My capital is now: " + str(capital))
        print("------------------------------")
        num_of_shares = 0
        long_implied_stop_price = 0
        last_ent_p = 0
        scaling_long_atr = 0


    return [in_position_long, long_stop_loss_price, long_implied_stop_price, capital, num_of_shares]




def exit_short_check(stock_data, capital):
    global in_position_short, short_stop_loss_price, short_implied_stop_price, last_ent_p, scaling_short_atr, total_pnl, pnl, num_of_shares

    if(stock_data[-1]['close'] > short_stop_loss_price):
        in_position_short = False
        pnl = calc_pnl(stock_data, last_ent_p, num_of_shares)
        total_pnl += pnl
        costs = round(num_of_shares * stock_data[-1]['close'], 2)
        capital += round(capital + costs, 2)
        print("Today's close price: " + str(stock_data[-1]['close']) + "  Today's date: " + stock_data[-1]['date'][0:10] + " In position: " + str(in_position_short))
        print("Stop loss hit: " + str(short_stop_loss_price))
        print("Go out while you can, exited short trade!)")
        print("My capital is now: " + str(capital))
        print("------------------------------")
        num_of_shares = 0
        short_stop_loss_price = 0
        last_ent_p = 0
        scaling_short_atr = 0

    elif(stock_data[-1]['close'] > short_implied_stop_price):
        in_position_short = False
        pnl = calc_pnl(stock_data, last_ent_p, num_of_shares)
        total_pnl += pnl_calc
        costs = round(num_of_shares * stock_data[-1]['close'], 2)
        capital += round(capital + costs, 2)
        print("Today's close price: " + str(stock_data[-1]['close']) + "  Today's date: " + stock_data[-1]['date'][0:10] + " In position: " + str(in_position_short))
        print("Implied stop hit: " + str(short_implied_stop_price))
        print("Go out while you can, exited long trade!)")
        print("My capital is now: " + str(capital))
        print("------------------------------")
        num_of_shares = 0
        short_implied_stop_price = 0
        last_ent_p = 0
        scaling_short_atr = 0


    return [in_position_short, short_stop_loss_price, short_implied_stop_price, capital, num_of_shares]

    
def scaling_long(stock_data, day_period, capital, r_perc):
    global long_stop_loss_price, long_implied_stop_price, last_ent_p, scaling_long_atr, total_pnl, pnl, num_of_shares

    scaling_long = False
    num_of_shares_scaling_long = 0
    atr = scaling_long_atr
    if(stock_data[-1]['close'] >= (last_ent_p + scaling_long_atr * 2)):
        scaling_long = True
        if (capital > 0):
            num_of_shares_scaling_long += int((capital * r_perc - comission) / (2 * atr))
            num_of_shares += num_of_shares_scaling_long
            costs = round(num_of_shares_scaling_long * stock_data[-1]['close'], 2)
            capital = round(capital - costs, 2)

        long_stop_loss_price = set_stop_loss_long(stock_data, day_period)
        long_implied_stop_price = set_implied_stop_long(stock_data, day_period)

        print("Today's close price: " + str(stock_data[-1]['close']) + "  Today's date: " + stock_data[-1]['date'][0:10] + "  In position: " + str(in_position_long) + "  Scaling long: " + str(scaling_long))
        print("The price for scaling was: " + str(last_ent_p + scaling_long_atr * 2))
        print("Go in and don't look back! Costs: " + str(costs))
        print("Stop loss: " + str(long_stop_loss_price) + " Implied Stop: " + str(long_implied_stop_price))
        print("And this is how much I have left: " + str(capital))
        #print("I am in this sh!t for long!!!!")
        print("Scaling long is working bitches!!!!")
        print("------------------------------")
        last_ent_p = stock_data[-1]['close']
    
    return [scaling_long, long_stop_loss_price, long_implied_stop_price, capital, num_of_shares]
    

    
    
def scaling_short(stock_data, day_period, capital, r_perc):
    global short_stop_loss_price, short_implied_stop_price, last_ent_p, scaling_short_atr, total_pnl, pnl, num_of_shares

    scaling_short = False
    num_of_shares_scaling_short = 0
    atr = scaling_short_atr
    if(stock_data[-1]['close'] <= (last_ent_p - scaling_short_atr * 2)):
        scaling_short = True
        if (capital > 0):
            num_of_shares_scaling_short += int((capital * r_perc - comission) / (2 * atr))
            num_of_shares += num_of_shares_scaling_short
            costs = round(num_of_shares_scaling_short * stock_data[-1]['close'], 2)
            capital = round(capital - costs, 2)

        short_stop_loss_price = set_stop_loss_short(stock_data, day_period)
        short_implied_stop_price = set_implied_stop_short(stock_data, day_period)

        print("Today's close price: " + str(stock_data[-1]['close']) + "  Today's date: " + stock_data[-1]['date'][0:10] + "  In position: " + str(in_position_short) + "  Scaling short: " + str(scaling_short))
        print("The price for scaling was: " + str(last_ent_p - scaling_short_atr * 2))
        print("Go in and don't look back! Costs: " + str(costs))
        print("Stop loss: " + str(short_stop_loss_price) + " Implied Stop: " + str(short_implied_stop_price))
        print("And this is how much I have left: " + str(capital))
        #print("I am in this sh!t for long!!!!")
        print("Scaling short is working bitches!!!!")
        print("------------------------------")
        last_ent_p = stock_data[-1]['close']
    
    return [scaling_long, long_stop_loss_price, long_implied_stop_price, capital, num_of_shares]
    





#stockdata = get_hystory_data('SPY', 2)
#entry_long_check(stockdata, s1_period)
