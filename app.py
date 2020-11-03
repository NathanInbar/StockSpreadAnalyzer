from flask import Flask, render_template, request
from flask_session import Session
from alpha_vantage.timeseries import TimeSeries
import json

#relavant docs: https://www.alphavantage.co/documentation/#intraday

#alpha vantage api key
API_KEY="O3QZG39MGA8IMI1R"

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
Session(app)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        symbol = request.form.get('symbol')
        return render_template("index.html", result=symbol)        

app.run(debug=True)
