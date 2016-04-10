import json
import requests
import twilio
import flask
from flask import Flask, request
from twilio import twiml
from string import Template

with open('config.json', 'r') as config_file:
    config_string = config_file.read()
    config = json.loads(config_string)

quandl_key = config.get('quandl_key')
message_templates = config.get('message_templates')

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

def twiml_response(message, phone_number):
    twilio_resp = twilio.twiml.Response()
    twilio_resp.addSms(message, to=phone_number)
    response = flask.Response(str(twilio_resp))
    response.headers['Content-Type'] = 'text/xml'
    return response

def get_help_twiml(phone_number):
    help_message = message_templates.get('help_message')
    return twiml_response(help_message, phone_number)

def get_quote_twiml(symbol, phone_numer):
    quote = get_stock_quote('WIKI', symbol).get('Close')
    print(quote)
    return twiml_response(quote, phone_number)

app = Flask(__name__)

@app.route('/sms', methods=['POST'])
def recieve_text():
    number = request.form['from']
    text = request.form['Body']
    if text[0] == '$':
        response_twiml = get_quote_twiml(text[1:], number)
    else:
        response_twiml = get_help_twiml(number)
    return response_twiml

@app.route('/quote')
def quote():
    q = get_stock_quote('WIKI','MSFT').get('Close')
    print(q)
    return str(q)


if __name__ == '__main__':
    app.run(debug=True)
