from flask import Flask, render_template, request
from flask_session import Session
from api_key import API_KEY
from datetime import date
from alpha_vantage.timeseries import TimeSeries
import numpy as np
from math import trunc
import json

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
Session(app)

ts = TimeSeries(key=API_KEY, output_format="pandas")

def split_dataframe(df, chunk_size):
    chunks = list()

    for i in range(len(df)):

        if len(df[i:i+chunk_size]) is 5:
            chunks.append(df[i:i+chunk_size])
        else:
            chunks.append(df[i:])
            break;

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

        highest_price = largest_swing_df['4. close'].max()
        lowest_price = largest_swing_df['4. close'].min()
        swing = truncate(largest_swing, 2)
        swing_percent = str.join('',f'{truncate(((1-(lowest_price/highest_price))*100), 2)}%')
        swing_date=f"{largest_swing_df.index[-1].date()} - {largest_swing_df.index[0].date()}"

        return render_template("index.html", highest_price=highest_price, lowest_price=lowest_price, swing=swing, swing_percent=swing_percent, date=swing_date)        

app.run()
