import requests
import json
import sys


# paths
FLOW_COLOR = '/flowcolor/{0}/'

DOMAIN = 'http://localhost:5000/api'

COLOR_IDS = {
    0: 'voltage low',
    1: 'voltage medium',
    2: 'voltage high',
    3: 'load normal',
    4: 'load high',
    5: 'load critical',
}

def print_msg():
    print 'python new_color.py <color id: 0-5> <color: RGB hex string>\n',  \
        ' Voltage color ids\n  0 - Low\n  1 - Medium\n  2 - High\n',        \
        ' Load color ids\n  3 - Normal\n  4 - High\n  5 - Critical\n\n',    \
        ' Color hex string example:\n  ff0000 - Red\n  00ff00 - Green\n'


def put(path, content):
    url = DOMAIN + path
    try:
        response = requests.put(url, json=content)
    except:
        print 'Unable to connect to app, make sure the application is running!'
        return
    try:
        return response.json()
    except:
        print 'status {0}, content:\n'.format(response.status_code, response.text)

def set_color(id, rgb):
    id = int(id)
    if id in COLOR_IDS:
        print 'set color for {0} to: {1}'.format(COLOR_IDS.get(id), rgb)
        put(FLOW_COLOR.format(id), {'rgb': rgb})
    else: 
        print_msg()



if __name__ == '__main__':
    if len(sys.argv) is not 3:
        print_msg()
    else:
        set_color(sys.argv[1], sys.argv[2])
    