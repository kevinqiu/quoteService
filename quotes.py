import json
import Quandl
from string import Template

with open('config.json', 'r') as config_file:
    config_string = config_file.read()
    config = json.loads(config_string)

quandl_key = config.get('quandl_key')
params = [('api_key', quandl_key), ('rows', 1)]
sym = 'msft'
query_string = 'WIKI/' + sym

data = Quandl.get(query_string, authtoken=quandl_key,rows=1,returns='numpy')

