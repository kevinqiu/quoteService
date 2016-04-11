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
max_quotes = int(config.get('max_quotes'))

# String, String -> Unit
def save_symbols(number, syms):
    NumberEntry = Query()
    number_symbol_entry = { 'number': number, 'symbols': syms }
    updated = db.update(number_symbol_entry, NumberEntry.number == number)
    if len(updated) == 0:
        db.insert(number_symbol_entry)
    logging.info('Symbols saved for ', number)
    return

# String -> List[String]
def retrieve_symbols(number):
    logging.info('Retrieving symbols for ', number)
    NumberEntry = Query()
    results = db.search(NumberEntry.number == number)
    return results[0]['symbols'] if len(results) > 0 else []

# string -> SymbolObj
# makes request to markitondemand api for symbols
# SymbolObj is a dictionary with keys symbol and price
def get_stock_quote_markit(sym):
    markitUrl = 'http://dev.markitondemand.com/MODApis/Api/v2/Quote/json'
    params = {'symbol': sym }
    result = requests.get(markitUrl, params=params).json()
    price = result.get('LastPrice')
    return { 'symbol': sym,
             'price': result.get('LastPrice') }
# SymbolObj -> String
def format_quote(quote):
    quote_tmp = Template(message_templates.get('quote_template'))
    if quote['price'] != None:
        price = quote['price']
    else:
        price = 'Invalid Symbol'
    return quote_tmp.substitute(symbol = quote['symbol'], price = price)

# List[SymbolObj] -> String
def format_quotes(quotesList):
    quote_strings = list(map(format_quote, quotesList))
    return ', '.join(quote_strings)

# SymbolObj -> Bool
def validQuote(quote):
    return quote['price'] != None

# List[String] -> String
def get_formatted_quotes(symbolList):
    logging.info('Retrieving quotes for ', symbolList)
    quotes =  list(map(get_stock_quote_markit, symbolList))
    return format_quotes(quotes)

# String, String -> flask.Response
def twiml_sms_response(message, phone_number):
    twilio_resp = twilio.twiml.Response()
    twilio_resp.addSms(message, to=phone_number)
    response = flask.Response(str(twilio_resp))
    response.headers['Content-Type'] = 'text/xml'
    return response

# String -> List[String]
def extract_symbols(text):
    symbols = re.findall(r'\$(\w*)', text)
    return list(set(map(str.upper, symbols)))

# load saved symbols or
# extract symbols from message
def get_symbols(number, text):
    if bool(re.match('last', text, re.I)):
        symbols = retrieve_symbols(number)
    else:
        symbols = extract_symbols(text)
    return symbols

app = Flask(__name__)

@app.route('/sms', methods=['POST'])
def recieve_text():
    number = request.form['From']
    text = request.form['Body']
    symbols = get_symbols(number, text)

    if len(symbols) > max_quotes:
        max_template = Template(message_templates.get('max_exceeded'))
        max_reached_notice = max_template.substitute(max_quotes = max_quotes)
        message = max_reached_notice
    elif len(symbols) > 0:
        try:
            save_symbols(number, symbols)
        except:
            #log save error
            logging.error('Could not save symbols for number', number)
        try:
            message = get_formatted_quotes(symbols)
        except:
            message = message_templates.get('error_message')
    else:
        message = message_templates.get('help_message')
    return twiml_sms_response(message, number)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
