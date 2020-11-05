from flask import Flask, render_template, request
from flask_session import Session
from api_key import API_KEY
from datetime import date
from alpha_vantage.timeseries import TimeSeries
import numpy as np
from math import trunc
#import matplotlib.pyplot as plt
import json

#relavant docs: https://www.alphavantage.co/documentation/#intraday

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
Session(app)

ts = TimeSeries(key=API_KEY, output_format="pandas")

def split_dataframe(df, chunk_size):
    chunks = list()
    # num_chunks = len(df) // chunk_size+1
    # for i in range(num_chunks):
    #     chunks.append(df[i*chunk_size:(i+1)*chunk_size])

    for i in range(len(df)):
        #print(i)
        #try:
            #try to append i through i+chunk
        if len(df[i:i+chunk_size]) is 5:
            chunks.append(df[i:i+chunk_size])
        else:
            chunks.append(df[i:])
            break;
        #except IndexError:
            #if index is out of bounds append a chunk that covers the rest of the dataframe
            #chunks.append(df[i:])
    #print(chunks)
    return chunks

def truncate(number, digits) -> float:
    stepper = 10.0 ** digits
    return trunc(stepper * number) / stepper

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html", highest_price="-", lowest_price="-", swing="-", swing_percent="-")

    if request.method == "POST":
        #get the form values
        symbol = request.form.get('symbol')
        startdate = request.form.get('startdate').split('-')
        enddate = request.form.get('dt').split('-')
        swingduration = request.form.get('swingduration')

        #convert start/end dates into integers
        for i in range(0,len(startdate)):
            startdate[i] = int(startdate[i])
        for i in range(0,len(enddate)):
            enddate[i] = int(enddate[i])

        #start and end date converted into readable format for dataframe truncation
        strt = date(startdate[0],startdate[1],startdate[2])
        end = date(enddate[0],enddate[1],enddate[2])
        print(f"S: {strt} \nE: {end}")
        #will hold the high/low points of the data slices


    #try:
        #load all of the stock data into the pandas dataframe
        data, meta_data = ts.get_daily_adjusted(symbol=symbol,outputsize="full")
        #truncate the dataframe to hold only the dat between start and end date
        data = data.truncate(before=strt, after=end)
        #slice the dataframe into chunks of the request size (given in days) after reversing the order
        sliced_data = split_dataframe(data, int(swingduration))
        #find the high/lows of those chunks
        largest_swing = -1
        largest_swing_df = None
        for df in sliced_data:
            current_swing = df['4. close'].max() - df['4. close'].min()
            if current_swing > largest_swing:
                largest_swing = current_swing
                largest_swing_df = df
                print("LARGEST:",largest_swing_df)
            #highs.append(df['4. close'].max())
            #lows.append(df['4. close'].min())

    #except Exception as e:
        #print(f'error:{e}')
        #return render_template("index.html", highest_price="ERR")

        #print(f"\nD:{data}")
        #print(f"H: {highs} \nL: {lows}")
        #calculate values to be returned to index.html
        highest_price = largest_swing_df['4. close'].max()
        lowest_price = largest_swing_df['4. close'].min()
        swing = truncate(largest_swing, 2)
        swing_percent = str.join('',f'{truncate(((1-(lowest_price/highest_price))*100), 2)}%')
        swing_date=f"{largest_swing_df.index[-1].date()} - {largest_swing_df.index[0].date()}"
        #date=

        return render_template("index.html", highest_price=highest_price, lowest_price=lowest_price, swing=swing, swing_percent=swing_percent, date=swing_date)        


app.run(debug=True)
