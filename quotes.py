import json
import urllib.parse
import urllib.request
from string import Template

with open('config.json', 'r') as config_file:
    config_string = config_file.read()
    config = json.loads(config_string)

quandl_key = config.get('quandl_key')
query_template = Template('https://www.quandl.com/api/v3/datasets/WIKI/$symbol/data.json?$param_string')
params = [('api_key', quandl_key), ('rows', 1)]
param_string = urllib.parse.urlencode(params)
url = query_template.substitute(symbol = 'MSFT', param_string = param_string)
result_string = urllib.request.urlopen(url).read()

def construct_stock_info(result_string):
    response_data = json.loads(result_string).get('dataset_data')
    headers = response_data.get('column_names')
    data_row = response_data.get('data')[0]
    return dict(zip(headers, data_row))
