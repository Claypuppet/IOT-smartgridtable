import requests
import json
import sys
import time

TABLE_PART_LIST = '/tableparts/'
TABLE_PART_MODULES = '/tableparts/{0}/modules/'
TABLE_PART_NEIGHBORS = '/tableparts/{0}/neighbors/'
MODULE_LIST = '/modules/'
MODULE_INFO = '/modules/{0}/'
MODULE_CONFIG_LIST = '/modules/{0}/configs/'
MODULE_CONFIG_INFO = '/modules/{0}/configs/{1}/'
FLOW_COLOR = '/flowcolor/{0}/'

DOMAIN = 'http://localhost:5000/api'

def get(path):
    url = DOMAIN + path
    response = requests.get(url)
    try:
        return response.json()
    except:
        print 'unable to parse json:\n', response.text
        return {}

def put(path, content):
    url = DOMAIN + path
    response = requests.put(url, json=content)
    try:
        return response.json()
    except:
        print 'status {0}, content:\n'.format(response.status_code, response.text)
        return {}

def setValue(home_consumption_percentage, factory_consumption_percentage, solar_percentage, wind_percentage):
    
    modules = get(MODULE_LIST).get("modules", [])
    for module in modules:
        module_id = module.get("id", 0)
        module_configs = get(MODULE_CONFIG_LIST.format(module_id)).get("configurations", [])
        for config in module_configs:
            module_configuration = get(MODULE_CONFIG_INFO.format(module.get("id"), config.get("id")))
            if int(module_configuration['id']) in [1, 2]:
                config_max = module_configuration.get("max", 0)
                new_value = int(config_max * home_consumption_percentage)
                put(MODULE_CONFIG_INFO.format(module.get("id"), config.get("id")), {'value':new_value})
            if int(module_configuration['id']) in [7]:
                config_max = module_configuration.get("max")
                new_value = int(config_max * factory_consumption_percentage)
                put(MODULE_CONFIG_INFO.format(module.get("id"), config.get("id")), {'value':new_value})
            elif int(module_configuration['id']) in [8]:
                config_max = module_configuration.get("max")
                new_value = int(config_max * solar_percentage)
                put(MODULE_CONFIG_INFO.format(module.get("id"), config.get("id")), {'value':new_value})
            elif int(module_configuration['id']) in [4, 5, 6]:
                config_max = module_configuration.get("max")
                new_value = int(config_max * wind_percentage)
                put(MODULE_CONFIG_INFO.format(module.get("id"), config.get("id")), {'value':new_value})

def simulate_network():
    four_hour_sleep = 9 # seconds
    while True:
        try:
            # 00:00
            print '00:00'
            setValue(0.3, 0.2, 0.05, 0.1)
            time.sleep(four_hour_sleep)
            # 04:00
            print '04:00'
            setValue(0.8, 0.3, 0.1, 0.1)
            time.sleep(four_hour_sleep);
            # 08:00
            print '08:00'
            setValue(0.8, 0.3, 0.2, 0.3)
            time.sleep(four_hour_sleep);
            # 12:00
            print '12:00'
            setValue(0.2, 1, 1, 0.4)
            time.sleep(four_hour_sleep)
            # 16:00
            print '16:00'
            setValue(1, 0.8, 0.5, 1)
            time.sleep(four_hour_sleep)
            # 20:00
            print '20:00'
            setValue(1, 0.3, 0.05, 0.6)
            time.sleep (four_hour_sleep)
        except KeyboardInterrupt as e:
            print '\nNetwork simulation STOP!'
            break


if __name__ == '__main__':
    print 'Network simulation START!'
    simulate_network()
