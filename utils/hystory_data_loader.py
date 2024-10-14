import json
import requests
from datetime import date

stock_data = []

# Uploading all the historical data to a new file 
def get_hystory_data_chunk(ticker, date_to):
    global stock_data
    results = requests.get("http://api.marketstack.com/v1/eod?access_key=551f53cae1c33fb718c327b55a80c5d8&symbols=" + 
        ticker + "&date_to=" + str(date_to))

    data = results.json()
    stock_data = stock_data + data['data']

    first_day = data['data'][-1]['date'][0:10]
    print(first_day)

    return first_day


def get_hystory_data(ticker, time_frame):
    global stock_data

    #first_day = date(2024, 1, 4)
    first_day = date.today()
    print(first_day)

    for i in range(time_frame):
        first_day = get_hystory_data_chunk(ticker, first_day)

    file = open('hystoryData/' + ticker + '.json', 'w')
    file.write(json.dumps(stock_data))
    file.close()

    return stock_data


#get_hystory_data('SPY', 2)