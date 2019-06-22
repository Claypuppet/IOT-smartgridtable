import requests
import json
import sys
import time

from values_for_testing import *


# paths
TABLE_SECTION_LIST = '/tablesections/'
TABLE_SECTION_MODULES = '/tablesections/{0}/modules/'
TABLE_SECTION_NEIGHBORS = '/tablesections/{0}/neighbors/'
MODULE_LIST = '/modules/'
MODULE_INFO = '/modules/{0}/'
MODULE_CONFIG_LIST = '/modules/{0}/configs/'
MODULE_CONFIG_INFO = '/modules/{0}/configs/{1}/'
FLOW_COLOR = '/flowcolor/{0}/'
POWER_BOUNDARIES = '/powerboundaries/'

DOMAIN = 'http://localhost:5000/api'

def get(path):
    url = DOMAIN + path
    response = requests.get(url)
    try:
        print response.status_code
        return response.json()
    except:
        print path, 'unable to parse json:\n', response.text
        return ''

def put(path, content):
    url = DOMAIN + path
    response = requests.put(url, json=content)
    try:
        print response.status_code
        return response.json()
    except:
        print 'status {0}, content:\n'.format(response.status_code, response.text)
        return ''

def post(path, content):
    url = DOMAIN + path
    response = requests.post(url, json=content)
    try:
        return response.json()
    except:
        print 'status {0}, content:\n'.format(response.status_code, response.text)

def call_flask_api():

    # TODO: create assert tests?
    print get(TABLE_SECTION_LIST)
    print get(TABLE_SECTION_MODULES.format(table_1_id))
    print get(TABLE_SECTION_NEIGHBORS.format(table_2_id))
    print get(MODULE_LIST)
    print get(MODULE_INFO.format(module_low))
    print get(MODULE_CONFIG_LIST.format(module_low))
    print get(MODULE_CONFIG_INFO.format(module_low, 2))
    print put(MODULE_CONFIG_INFO.format(module_low, 2), {'value': 5})
    print put(FLOW_COLOR.format(0), {'rgb': 'ff0000'})
    print get(POWER_BOUNDARIES) 
    print put(POWER_BOUNDARIES, {'voltage': 0, 'load': 2, 'value': 500})

    print '\n All tests successful\n'


if __name__ == '__main__':
    if len(sys.argv) is 2:
        DOMAIN = sys.argv[1]
    call_flask_api()
    