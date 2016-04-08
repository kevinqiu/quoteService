import json
import requests
from twilio.rest import TwilioRestClient
from string import Template

with open('config.json', 'r') as config_file:
    config_string = config_file.read()
    config = json.loads(config_string)

quandl_key = config.get('quandl_key')

def quandl_url(db, sym):
    return 'https://www.quandl.com/api/v3/datasets/'+ db+ '/' + sym + '/data.json'

def parse_stock_info(result_json):
    response_data = result_json.get('dataset_data')
    headers = response_data.get('column_names')
    data_row = response_data.get('data')[0]
    return dict(zip(headers, data_row))

def get_stock_quote(db, sym):
    params = {'api_key':quandl_key, 'rows': 1}
    url = quandl_url(db, sym)
    result = requests.get(url, params=params).json()
    return parse_stock_info(result)

from flask import Flask
app = Flask(__name__)

@app.route("/quote")
def quote():
    get_stock_quote('WIKI','MSFT')

if __name__ == "__main__":
    app.run()
