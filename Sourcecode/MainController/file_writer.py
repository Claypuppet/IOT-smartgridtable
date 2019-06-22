import os
import json


def read_contents_from_file(file):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, file)
    with open(file_path) as data_file:
        data = json.load(data_file)
    return data


def save_module_config(file, module_id, config_id, value):
    data = read_contents_from_file(file)
    for module in data['modules']:
        if module_id != module['id']:
            continue

        configurations = module['configurations']
        for configuration in configurations:
            if configuration['type'] is config_id:
                configuration['value'] = str(value)
                break
        break
    data = json.dumps(data, indent=2, separators=(',', ': '))
    write_contents_to_file(file, data)


def write_contents_to_file(file, data):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, file)
    with open(file_path, 'w') as data_file:
        data_file.write(data)
