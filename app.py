from flask import Flask, render_template, request
from flask_session import Session
from api_key import API_KEY
from datetime import datetime
from iexfinance.stocks import get_historical_data 
import json

#relavant docs: https://www.alphavantage.co/documentation/#intraday

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
Session(app)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        symbol = request.form.get('symbol')
        startdate = request.form.get('startdate').split('-')
        enddate = request.form.get('dt').split('-')
        swingduration = request.form.get('swingduration')

        for i in range(0,len(startdate)):
            startdate[i] = int(startdate[i])

        for i in range(0,len(enddate)):
            enddate[i] = int(enddate[i])

        strt = datetime(startdate[0],startdate[1],startdate[2])
        end = datetime(enddate[0],enddate[1],enddate[2])

        strt = datetime(2019,1,1)
        end = datetime(2019,1,2)

        data = {}

        try:
            #data = get_historical_data(symbol,strt, end, token=API_KEY)
            data = get_historical_data("TSLA",strt,end, token=API_KEY)
        except Exception as e:
            print(f'error:{e}')

        print('debug')
        for key in data:
            print(data[key]['high'])


        #print(f'S: {symbol}\nSD: {startdate}\nED: {enddate}\nSW: {swingduration}\n')
        return render_template("index.html", result=symbol)        


app.run(debug=True)
