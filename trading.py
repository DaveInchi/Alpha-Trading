import json
import requests
from utils.atr_calc import calc_atr
from utils.hystory_data_loader import get_hystory_data

s1_period = 20
in_position_long = False
in_position_short = False
stop_loss_price = 0
implied_stop_price = 0

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
        if(stock_data[i]['close'] > lowest_price):
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


def set_implied_stop_long(stock_data, day_period):
    array = []
    for i in range(0, (day_period - 1)):
        array.append(stock_data[i]['close'])
    array = array[int(len(array) / 2):]
    return min(array)


def set_implied_stop_short(stock_data, day_period):
    array = []
    for i in range(0, (day_period - 1)):
        array.append(stock_data[i]['close'])
    array = array[int(len(array) / 2):]
    return max(array)



def entry_long_check(stock_data, day_period, capital, num_of_shares, r_perc):
    global in_position_long, stop_loss_price, implied_stop_price

    highest_price = get_highest_price(stock_data, day_period - 1)
    
    
    if(stock_data[-1]['close'] > highest_price):
        in_position_long = True

        if(capital > 0):
            atr = calc_atr(stock_data, day_period)
            num_of_shares = int((capital * 0.5 * r_perc) / (2 * atr))
            costs = round(num_of_shares * stock_data[-1]['close'], 2)
            capital = round(capital - costs, 2)

        stop_loss_price = set_stop_loss_long(stock_data, day_period)
        implied_stop_price = set_implied_stop_long(stock_data, day_period)

        print("Today's close price: " + str(stock_data[-1]['close']) + "  Today's date: " + stock_data[-1]['date'][0:10] + " In position: " + str(in_position_long))
        #print("Highest price: " + str(highest_price))
        print("Go in and don't look back! Costs: " + str(costs))
        print("Stop loss: " + str(stop_loss_price) + " Implied Stop: " + str(implied_stop_price))
        print("And this is how much I have left: " + str(capital))
        print("I am in this sh!t for long!!!!")
        print("------------------------------")
    

    return [in_position_long, stop_loss_price, implied_stop_price, capital, num_of_shares]


def exit_long_check(stock_data, capital, num_of_shares):
    global in_position_long, stop_loss_price, implied_stop_price

    if(stock_data[-1]['close'] < stop_loss_price):
        in_position_long = False
        capital = capital + (num_of_shares * stock_data[-1]['close'])
        num_of_shares = 0
        print("Today's close price: " + str(stock_data[-1]['close']) + "  Today's date: " + stock_data[-1]['date'][0:10] + " In position: " + str(in_position_long))
        print("Stop loss hit: " + str(stop_loss_price))
        print("Go out while you can!)")
        print("My capital is now: " + str(capital))
        print("------------------------------")
        stop_loss_price = 0

    elif(stock_data[-1]['close'] < implied_stop_price):
        in_position_long = False
        capital = capital + (num_of_shares * stock_data[-1]['close'])
        num_of_shares = 0
        print("Today's close price: " + str(stock_data[-1]['close']) + "  Today's date: " + stock_data[-1]['date'][0:10] + " In position: " + str(in_position_long))
        print("Implied stop hit: " + str(implied_stop_price))
        print("Go out while you can!)")
        print("My capital is now: " + str(capital))
        print("------------------------------")
        implied_stop_price = 0


    return [in_position_long, stop_loss_price, implied_stop_price, capital, num_of_shares]



#stockdata = get_hystory_data('SPY', 2)
#entry_long_check(stockdata, s1_period)
