from flask import Flask, request, jsonify
from flask.views import MethodView

from smart_grid_table import *
from smart_grid_messaging import *
from settings import Side, COLOR_DICT, VOLTAGE_POWER_LOAD_BOUNDARIES

_smart_grid_table = None
_add_message_func = None

class InvalidId(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv



class TableSectionView(MethodView):
    def get(self):
        global _smart_grid_table
        tps = _smart_grid_table.get_table_sections()
        data = {
            "table_sections": [{
                "id": tp.get_id(),
                "type": tp.get_type()
            } for tp in tps]
        }
        return jsonify(data)


class TableSectionModuleView(MethodView):
    def get(self, table_section_id):
        global _smart_grid_table
        tp = _smart_grid_table.get_table_section(table_section_id)
        if tp is None:
            raise InvalidId('Table Section {0} does not exist'.format(table_section_id), status_code=410)
        modules = [mf.get_module(False) for mf in tp.get_flows(ModuleFlowSegment)]
        data = {
            "modules": [{
                "id": m.get_id(),
                "locationId": location 
            } for location, m in enumerate(modules) if m is not None]
        }

        return jsonify(data)


class TableSectionNeighborView(MethodView):
    def get(self, table_section_id):
        global _smart_grid_table
        tp = _smart_grid_table.get_table_section(table_section_id)
        if tp is None:
            raise InvalidId('Table Section {0} does not exist'.format(table_section_id), status_code=410)
        neighbors = tp.get_neighbors()
        data = {
            "neighbors":[{
                "side": Side.enum_to_str(side), 
                "id": nb.get_id()
                } for side, nb in neighbors.iteritems() if nb is not None
            ]
        }
        return jsonify(data)


class ModuleView(MethodView):
    def get(self, module_id=None):
        global _smart_grid_table
        if module_id is None:
            modules = _smart_grid_table.get_modules()
            data = {
                "modules":[{
                    "id": m.get_id()
                } for m in modules if isinstance(m, DefaultModule)],
                "transformers":[{
                    "id": m.get_id()
                } for m in modules if isinstance(m, ConnectionModule)]
            }
            return jsonify(data)
        else:
            module = _smart_grid_table.get_module(module_id)
            if module is None:
                raise InvalidId('Module {0} does not exist'.format(module_id), status_code=410)
            data = {
                "id": module.get_id(),
                "name": module.get_name(),
                "voltage": module.get_voltage(string=True),
                "power": module.get_power(),
            }
            return jsonify(data)


class ModuleConfigView(MethodView):
    def get(self, module_id, config_id=None):
        global _smart_grid_table
        module = _smart_grid_table.get_module(module_id)
        if module is None:
            raise InvalidId('Module {0} does not exist'.format(module_id), status_code=410)

        if config_id is None:
            configs = module.get_configurations()
            data = {
                "configurations":[{
                    "id": config.get_config_id(),
                    "min": config.get_min_value(),
                    "max": config.get_max_value(),
                    "value": config.get_value(),
                    "name": config.get_name(),
                    "role": config.get_role(string=True)
                } for config in configs]
            }
            return jsonify(data)
        else:
            config = module.get_configuration(config_id)
            if config is None:
                raise InvalidId('Config {0} does not exist'.format(config_id), status_code=410)

            data = {
                "id": config.get_config_id(),
                "min": config.get_min_value(),
                "max": config.get_max_value(),
                "value": config.get_value(),
                "name": config.get_name(),
                "role": config.get_role(string=True)
            }
            return jsonify(data)

    def put(self, module_id, config_id):
        global _smart_grid_table

        module = _smart_grid_table.get_module(module_id)
        if module is None:
            raise InvalidId('Module {0} does not exist'.format(module_id), status_code=410)

        config = module.get_configuration(config_id)
        if config is None:
            raise InvalidId('Config {0} does not exist'.format(config_id), status_code=410)

        put_data = request.get_json()
        new_value = put_data.get('value')

        s_message = SmartMessage(
            MessageTypes.CONFIG_CHANGED,
            (module_id, config_id, new_value))

        _add_message_func(s_message)

        data = {
            "id": config.get_config_id(),
            "min": config.get_min_value(),
            "max": config.get_max_value(),
            "value": new_value,
            "name": config.get_name(),
            "role": config.get_role(string=True)
        }
        return jsonify(data)


class FlowSegmentColorView(MethodView):
    def put(self, color_id):
        color_ids = [COLOR_DICT[c]['id'] for c in COLOR_DICT]
        if color_id not in color_ids:
            raise InvalidId('Color id {0} does not exist'.format(color_id), status_code=410)

        put_data = request.get_json()
        rgb = put_data.get('rgb', '')

        if not self.valid_rgb(rgb):
            raise InvalidId('RGB {0} not valid'.format(rgb), status_code=410)

        s_message = SmartMessage(MessageTypes.COLOR_CHANGED, (color_id, rgb))
        _add_message_func(s_message)

        return jsonify(put_data)

    def valid_rgb(self, rgb):
        """
        RGB should be string of 6 characters. + check for hex string
        """
        if len(rgb) is 6:
            try:
                int(rgb, 16)
                return True
            except:
                pass
        return False


class PowerBoundaryView(MethodView):
    def get(self):
        data = {
            'boundaries': VOLTAGE_POWER_LOAD_BOUNDARIES
        }

        return jsonify(data)

    def put(self):
        put_data = request.get_json()
        voltage, load, value = put_data.get('voltage', None), put_data.get('load', None), put_data.get('value', None)
        if voltage not in VOLTAGE_POWER_LOAD_BOUNDARIES:
            raise InvalidId('Voltage {0} not supported'.format(voltage), status_code=410)
        if load not in VOLTAGE_POWER_LOAD_BOUNDARIES[voltage]:
            raise InvalidId('Load {0} not supported'.format(load), status_code=410)
        if not self.validate_value(value, load):
            raise InvalidId('Invalid value {0}'.format(value), status_code=410)

        s_message = SmartMessage(MessageTypes.POWER_BOUNDARIES_CHANGED, (voltage, load, value))
        _add_message_func(s_message)

        return jsonify(put_data)

    def validate_value(self, value, load):
        """
        value should be > 0 if load is critical, 
        value should be between 0-1 if load is high
        """
        if load is Load.HIGH:
            value = float(value)
            return True if value > 0 and value < 1 else False
        if load is Load.CRITICAL:
            value = int(value)
            return True if value > 0 else False
        return False



class ApiServer(Flask):
    def __init__(self, smart_grid_table, add_message_func):
        super(ApiServer, self).__init__(__name__)

        # Set smart grid table / message func so views can reach it
        global _smart_grid_table
        _smart_grid_table = smart_grid_table
        global _add_message_func
        _add_message_func = add_message_func

        # Add endpoints
        view_func = TableSectionView.as_view('table_sections')
        self.add_endpoint('/api/tablesections/', view_func, ['GET'])

        view_func = TableSectionModuleView.as_view('table_sections_modules')
        self.add_endpoint('/api/tablesections/<int:table_section_id>/modules/', view_func, ['GET'])

        view_func = TableSectionNeighborView.as_view('table_sections_neighbors')
        self.add_endpoint('/api/tablesections/<int:table_section_id>/neighbors/', view_func, ['GET'])

        view_func = ModuleView.as_view('modules')
        self.add_endpoint('/api/modules/', view_func, ['GET'])
        self.add_endpoint('/api/modules/<int:module_id>/', view_func, ['GET'])

        view_func = ModuleConfigView.as_view('modules_configs')
        self.add_endpoint('/api/modules/<int:module_id>/configs/', view_func, ['GET'])
        self.add_endpoint('/api/modules/<int:module_id>/configs/<int:config_id>/', view_func, ['GET', 'PUT'])

        view_func = FlowSegmentColorView.as_view('flow_colors')
        self.add_endpoint('/api/flowcolor/<int:color_id>/', view_func, ['PUT'])

        view_func = PowerBoundaryView.as_view('power_boundaries')
        self.add_endpoint('/api/powerboundaries/', view_func, ['GET', 'PUT'])

        @self.errorhandler(InvalidId)
        def handle_invalid_usage(error):
            response = jsonify(error.to_dict())
            response.status_code = error.status_code
            return response


    def add_endpoint(self, url, view_func, methods):
        self.add_url_rule(url, methods=methods, view_func=view_func)


if __name__ == "__main__":
    def print_msg(msg):
        print msg

    # Import test values
    from test_scripts.values_for_testing import *
        
    # Create table (also creates modules)
    table = SmartGridTable()

    # Connect a table (table_id, child_id, table_type)
    table.table_connected(table_1_id, None, None)
    table.table_connected(table_2_id, None, None)
    table.table_connected(table_3_id, None, None)
    table_section1 = table.get_table_section(table_1_id)
    table_section2 = table.get_table_section(table_2_id)
    table_section3 = table.get_table_section(table_3_id)

    # Place modules on Table Section (table_id, location_id, module_id)
    table.module_placed(table_1_id, module_location_west, module_low)
    table.module_placed(table_1_id, module_location_northwest, module_low2)
    table.module_placed(table_1_id, module_location_northeast, module_low3)

    # connect neighbor. table_neighbor_changed(table_id, location_id, connected_neighbor_id)
    table.table_neighbor_changed(table_1_id, table_conn_point_north, table_2_conn_south)
    table.table_neighbor_changed(table_2_id, table_conn_point_south, table_1_conn_north)

    # connect by transformers. module_placed(table_id, location_id, module_id)
    table.module_placed(table_3_id, module_location_east, transformer_high) # Place transformer high
    table.module_placed(table_2_id, module_location_west, transformer_mediumH) # Place transformer medium

    ApiServer(table, print_msg).run()
