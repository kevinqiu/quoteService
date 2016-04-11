import re
import json
import requests
import twilio
import flask
import tinydb
import logging
from tinydb import TinyDB, Query
from flask import Flask, request
from twilio import twiml
from string import Template

with open('config.json', 'r') as config_file:
    config_string = config_file.read()
    config = json.loads(config_string)

quandl_key = config.get('quandl_key')
message_templates = config.get('message_templates')
db = tinydb.TinyDB('db.json')

def save_symbols(number, syms):
    NumberEntry = Query()
    number_symbol_entry = { 'number': number, 'symbols': syms }
    updated = db.update(number_symbol_entry, NumberEntry.number == number)
    if len(updated) == 0:
        db.insert(number_symbol_entry)
    logging.info('Symbols saved for ', number)
    return

def retrieve_symbols(number):
    logging.info('Retrieving symbols for ', number)
    NumberEntry = Query()
    results = db.search(NumberEntry.number == number)
    return results[0]['symbols'] if len(results) > 0 else []

def get_stock_quote_markit(sym):
    markitUrl = 'http://dev.markitondemand.com/MODApis/Api/v2/Quote/json'
    params = {'symbol': sym }
    result = requests.get(markitUrl, params=params).json()
    price = result.get('LastPrice')
    return { 'symbol': sym,
             'price': result.get('LastPrice') }

def format_quote(quote):
    quote_tmp = Template(message_templates.get('quote_template'))
    if quote['price'] != None:
        price = quote['price']
    else:
        price = 'Invalid Symbol'
    return quote_tmp.substitute(symbol = quote['symbol'], price = price)

def format_quotes(quotesList):
    quote_strings = list(map(format_quote, quotesList))
    return ', '.join(quote_strings)

def validQuote(quote):
    return quote['price'] != None

def get_quotes(symbolList):
    logging.info('Retrieving quotes for ', symbolList)
    quotes =  list(map(get_stock_quote_markit, symbolList))
    return format_quotes(quotes)

def twiml_response(message, phone_number):
    twilio_resp = twilio.twiml.Response()
    twilio_resp.addSms(message, to=phone_number)
    response = flask.Response(str(twilio_resp))
    response.headers['Content-Type'] = 'text/xml'
    return response

def get_help_twiml(phone_number):
    help_message = message_templates.get('help_message')
    return twiml_response(help_message, phone_number)

def get_quotes_twiml(symbols, phone_number):
    quote = get_quotes(symbols)
    return twiml_response(quote, phone_number)

def extract_symbols(text):
    symbols = re.findall(r'\$(\w*)', text)
    return list(map(str.upper, symbols))

app = Flask(__name__)

@app.route('/sms', methods=['POST'])
def recieve_text():
    number = request.form['From']
    text = request.form['Body']

    if bool(re.match('last', text, re.I)):
        symbols = retrieve_symbols(number)
    else:
        symbols = extract_symbols(text)

    if len(symbols) > 0:
        try:
            save_symbols(number, symbols)
        except:
            logging.error('Could not save symbols for number', number)
            #log save error
        try:
            response_twiml = get_quotes_twiml(symbols, number)
        except:
            error = message_templates.get('error_message')
            response_twiml = twiml_response(error, number)
    else:
        response_twiml = get_help_twiml(number)
    return response_twiml


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
