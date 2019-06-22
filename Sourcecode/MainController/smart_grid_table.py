from settings import *
from logger import log
from table_section import *
from flow_segment import *
from module import *

import json


class SmartGridTable(object):
    """
    SmartGridTable 
    """
    def __init__(self):
        super(SmartGridTable, self).__init__()
        self.table_sections = []
        self.table_connection_ids = {}
        self.modules = []
        self.load_modules()
        self.load_table_info()
        
    def load_modules(self):
        self.modules = load_module_info()

    def load_table_info(self):
        self.table_sections, self.table_connection_ids = load_table_info()

    def get_module(self, id):
        return next((module for module in self.modules if module.id == id), None)

    def get_modules(self):
        return self.modules

    def get_table_section(self, id):
        return next((tp for tp in self.get_table_sections() if tp.id == id), None)

    def get_table_sections(self):
        return [tp for tp in self.table_sections if tp.is_connected()]

    def table_connected(self, table_id, location_id, payload):
        """
        A Table Section first connection to the main controller
        """
        table_section = next((tp for tp in self.table_sections if tp.id == table_id), None)
        if table_section is None:
            log('Unknown table with id {0} tried to connect'.format(table_id))
        elif not table_section.is_connected():
            log('New Table Section {0} connected'.format(table_id))
            table_section.set_connected(True)
        else:
            log('duplicate Table Section', table_section.id)
            table_section.clear_table()


    def module_config_changed(self, module_id, config_id, value):
        """
        Module configuration changed
        """
        module = self.get_module(module_id)
        if module is not None:
            module.save_configuration(config_id, value)
            if module.get_table_section() is not None:
                return True
        return False


    def table_neighbor_changed(self, table_id, location_id, connected_table_location_id):
        """
        A Table Section connects to another Table Section
        """ 

        connected_table_id = None

        if connected_table_location_id in self.table_connection_ids:
            connected_table_id = self.table_connection_ids[connected_table_location_id].get("table_id")
    
        table_section = next((tp for tp in self.get_table_sections() if tp.id == table_id), None)
        connected_table_section = next((tp for tp in self.table_sections if tp.id == connected_table_id), None)
        if table_section:
            log('On Table Section {0}, side {1}, table connected with id {2}'.format(table_id, location_id, connected_table_id))
            table_section.set_neighbor(location_id, connected_table_section)
            return True
        return False


    def module_placed(self, table_id, location_id, module_id):
        """
        A module is placed or removed from a Table Section
        """

        table_section = next((tp for tp in self.get_table_sections() if tp.id == table_id), None)
        module = next((m for m in self.modules if m.id == module_id), None)
        
        if module is None and module_id is not 0:
            log('Unknown module id "{0}" using None instead'.format(module_id))

        # Place module on table section
        if table_section:
            # Remove module if it's placed on a table section already
            if module is not None:
                tp = module.get_table_section()
                if tp is not None:
                    tp.remove_module(module)
                
            log('On Table Section {0}, module location {1}, module placed: {2}'.format(table_id, location_id, module))
            table_section.place_module(module, location_id)
            return True
        return False


    def flow_disabled(self, table_id, flow_id, disabled):
        """
        A module is placed or removed from a Table Section
        """
        table_section = next((tp for tp in self.get_table_sections() if tp.id == table_id), None)

        if table_section and flow_id in range(6):
            log('On Table Section {0}, flow location {1}, disabled: {2}'.format(table_id, flow_id, disabled))
            fs = [f for f in table_section.get_flows(RingFlowSegment) if not isinstance(f, NeighborFlowSegment)]
            fs[flow_id].set_force_disabled(disabled)

            # Check if voltage is not error, which means that table has ledstrip turned on
            if table_section.get_voltage() is not Voltages.ERROR:
                return True
        return False

    def get_flow_configurations(self):
        """
        Update all table parts:
            - Update state
            - Update load
            - Update direction
        Check for placed import/export module:
            - Create a better network for table section cluster using algorithms

        Return flow configurations for each table
        """
        connected_table_sections = self.get_table_sections()
        flow_configs = []

        # If there are Table Sections 
        if len(connected_table_sections) is 0:
            return flow_configs
        
        # Update all Table Section voltages based on placed transformer, and keep these in an array
        table_sections_with_transformer = []
        for table_section in connected_table_sections:
            table_section.update_voltage_by_transformer()
            if table_section.get_voltage() is not Voltages.ERROR:
                table_sections_with_transformer.append(table_section)

        # Sort upated Table Sections by voltage, lowest voltage first
        table_sections_with_transformer.sort(key=lambda x: x.get_voltage())

        for tp in table_sections_with_transformer:
            tp.update_voltage_for_neighbors(table_sections_with_transformer)

        for table_section in connected_table_sections:
            if table_section.get_voltage() is Voltages.ERROR:
                table_section.update_voltage()
            # Update module states now that the voltages are set
            table_section.update_module_flow_segments()

        # Sort table sections by voltage
        connected_table_sections = sorted(connected_table_sections, 
            key=lambda ts: ts.get_voltage(), reverse=True)

        # Update all Table Section flow states, module flow load/speed etc
        for table_section in connected_table_sections:
            table_section.update()


        # Get config
        for table_section in connected_table_sections:
            flow_config_string = ''.join(table_section.get_flow_bytes())
            flow_configs.append({
                'destination': table_section.get_id(),
                'config': flow_config_string
            })

        return flow_configs


if __name__ == '__main__':
    from test_scripts.smart_grid_table_test import start_tests
    start_tests()

