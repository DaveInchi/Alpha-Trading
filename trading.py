import json
import requests
from atr_calc import calc_atr
from hystory_data_loader import get_hystory_data


in_position = False
stop_loss = 0
implied_stop_price = 0

# Returns the highest closing price within the specified day period.
def get_highest_price(stock_data, day_period):
    highest_price = 0
    for i in range(day_period):
        if(stock_data[i]['close'] > highest_price):
            highest_price = stock_data[i]['close']
    return highest_price


# Returns the lowest closing price within the specified day period.
def get_lowest_price(stock_data, day_period):
    lowest_price = stock_data[0]['close']
    for i in range(day_period):
        if(stock_data[i]['close'] < lowest_price):
            lowest_price = stock_data[i]['close']
    return lowest_price


# Sets the implied stop price for long positions based on the lowest closing price.
def set_implied_stop_price_long(stock_data, day_period):
    global implied_stop_price
    implied_stop_price = stock_data[0]['close']
    for i in range(int(day_period)):
        if(stock_data[i]['close'] < implied_stop_price):
            implied_stop_price = stock_data[i]['close']


# Sets the implied stop price for short positions based on the highest closing price.
def set_implied_stop_price_short(stock_data, day_period):
    global implied_stop_price
    implied_stop_price = stock_data[0]['close']
    for i in range(int(day_period)):
        if(stock_data[i]['close'] > implied_stop_price):
            implied_stop_price = stock_data[i]['close']


# Checks if the current price has reached the implied stop price for long positions.
def implied_stop_check_long(stock_data):
    global in_position, implied_stop_price
    if(stock_data[0]['close'] <= implied_stop_price):
        in_position = False


# Checks if the current price has reached the implied stop price for short positions.
def implied_stop_check_short(stock_data):
    global in_position, implied_stop_price
    if(stock_data[0]['close'] >= implied_stop_price):
        in_position = False


# Sets the stop loss for long positions based on ATR and current closing price.
def set_stop_loss_long(stock_data, day_period):
    global stop_loss
    list_atr = calc_atr(stock_data, day_period)
    stop_loss = stock_data[0]['close'] - (list_atr[0] * 2)


# Sets the stop loss for short positions based on ATR and current closing price.
def set_stop_loss_short(stock_data, day_period):
    global stop_loss
    list_atr = calc_atr(stock_data, day_period)
    stop_loss = stock_data[0]['close'] + (list_atr[0] * 2)


# Checks if the current price has reached the stop loss level for long positions.
def stop_loss_check_long(stock_data):
    global in_position, stop_loss 
    if(stock_data[0]['close'] <= stop_loss):
        in_position = False


# Checks if the current price has reached the stop loss level for short positions.
def stop_loss_check_short(stock_data):
    global in_position, stop_loss
    if(stock_data[0]['close'] >= stop_loss):
        in_position = False


# Checks if conditions for entering a long position are met and sets stop loss and implied stop price.
def entry_long_check(stock_data, day_period): 
    global in_position, stop_loss, implied_stop_price
    highest_price = get_highest_price(stock_data, day_period)
    highest_price = 570
    print("Today's close price: " + str(stock_data[0]['close']) + "  Today's date: " + stock_data[0]['date'][0:10])
    print("Highest price: " + str(highest_price))
    
    if(stock_data[0]['close'] > highest_price):
        in_position = True
        set_stop_loss_long(stock_data, day_period)
        set_implied_stop_price_long(stock_data, day_period / 2)

    print("Stop loss: " + str(stop_loss) + " Implied Stop: " + str(implied_stop_price) + " in_position: " + str(in_position))


# Checks if conditions for entering a short position are met and sets stop loss and implied stop price.
def entry_short_check(stock_data, day_period): 
    global in_position, stop_loss, implied_stop_price
    lowest_price = get_lowest_price(stock_data, day_period)
    lowest_price = 550
    print("Today's close price: " + str(stock_data[0]['close']) + "  Today's date: " + stock_data[0]['date'][0:10])
    print("Lowest price: " + str(lowest_price))
    
    if(stock_data[0]['close'] < lowest_price):
        in_position = True
        set_stop_loss_short(stock_data, day_period)
        set_implied_stop_price_short(stock_data, day_period / 2)

    print("Stop loss: " + str(stop_loss) + " Implied Stop: " + str(implied_stop_price) + " in_position: " + str(in_position))








stockdata = get_hystory_data('SPY', 2)
entry_long_check(stockdata, 20)
