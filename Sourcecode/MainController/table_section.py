from settings import *
from file_writer import read_contents_from_file
from flow_segment import *
from grids import create_table_cluster
from logger import log


def load_table_info():
    """
    Load tables from the config/tableConfig.json file. 
    """
    table_connection_ids = {}
    table_sections = []

    data = read_contents_from_file(TABLE_CONFIG_FILE)
    for table_info in data.get("tableParts"):
        for side, connection_id in table_info.get("connections").iteritems():
            table_connection_ids[connection_id] = {
                "table_id": table_info.get("id"),
                "side": Side.str_to_enum(side)
            }
        table_sections.append(TableSection(
            int(table_info.get("id")),
            int(table_info.get("type"))))

    return table_sections, table_connection_ids


def get_most_common_voltage_from_list(voltages):
    """
    Return most common voltage from list of voltages. If the list of voltages is
    empty, return Error voltage.
    """
    if len(voltages) is 0:
        return Voltages.ERROR

    return max(set(voltages), key=voltages.count)



class TableSection(object):
    """
    Table Section object, contains flow structure
    """

    def __init__(self, id, table_type):
        super(TableSection, self).__init__()
        """
        Init Table Section, set id, table type and flows based on table type
        """

        # Set fields
        self.id = id
        self.type = table_type
        self.voltage = Voltages.ERROR
        self.voltage_level = VoltageLevel.NORMAL
        self.connected = False

        # Set flows (TODO: replace with graph structure in near future)
        if table_type == 1: # final table design
            self.flows = [
                ConnectionModuleFlowSegment(), RingFlowSegment(), ModuleFlowSegment(), NeighborFlowSegment(Side.NORTH),
                RingFlowSegment(Side.NORTH), NeighborFlowSegment(Side.NORTH), ModuleFlowSegment(), RingFlowSegment(),
                ConnectionModuleFlowSegment(), RingFlowSegment(), ModuleFlowSegment(), NeighborFlowSegment(Side.SOUTH),
                RingFlowSegment(Side.SOUTH), NeighborFlowSegment(Side.SOUTH), ModuleFlowSegment(), RingFlowSegment()
            ]
        else: # Unknown table type
            log('Unknown table type initiated', table_type)
            self.flows = []

        # If a neigbor connection is made, but the main controller has not received 
        # the connection from the neighbor yet, it will be temporarily saved in this
        # dict. This can either be a transformer object or table object.
        self.temporary_neighbors = {
            Side.NORTH: None,
            Side.EAST: None,
            Side.SOUTH: None,
            Side.WEST: None
        }

        # Neighbor connections (table objects)
        self.neighbors = {
            Side.NORTH: None,
            Side.EAST: None,
            Side.SOUTH: None,
            Side.WEST: None
        }

    def set_connected(self, connected):
        """
        Set table section connected
        """
        self.connected = connected

    def is_connected(self):
        """
        Return table section connected
        """
        return self.connected

    def get_id(self):
        """
        Return table section id
        """
        return self.id

    def get_type(self):
        """
        Return table section type
        """
        return self.type

    def get_neighbors(self, temporary=False):
        """
        Return table section neighbors
        """
        return self.temporary_neighbors if temporary else self.neighbors

    def get_placed_modules(self, module_type=None, no_error_state=False):
        """
        Returns placed modules based on given module type, default on all modules
        """ 
        module_type = module_type if module_type else Module
        flow_type = ConnectionModuleFlowSegment if module_type is ConnectionModule else ModuleFlowSegment
        flows = self.get_flows(flow_type)

        modules = [mf.get_module(no_error_state) for mf in flows if isinstance(mf.get_module(no_error_state), module_type)]

        return modules

    def get_flows(self, flow_type=None):
        """
        Returns flows based on given flow type, default on all flows
        """ 
        flow_type = flow_type if flow_type else FlowSegment
        return [f for f in self.flows if isinstance(f, flow_type)]

    def set_voltage(self, voltage):
        self.voltage = voltage
        for f in self.flows:
            f.set_voltage(voltage)

    def get_voltage(self, string=False):
        return Voltages.enum_to_str(self.voltage) if string else self.voltage

    def clear_table(self):
        """
        Remove all modules and neighbors from the table
        """
        for flow in self.get_flows(ModuleFlowSegment):
            flow.set_module(None)
        for side in self.neighbors:
            self.remove_neighbor_connection(side=side)
        
    def place_module(self, module, location):
        """
        Place given module on given location, if module is transformer, update 
        neighbors
        """
        if location in TABLE_PART[self.type]['module_locations']:
            module_flows = self.get_flows(ModuleFlowSegment)

            module_flows[location].set_module(module)

            if module is not None:
                # Set this table on the module
                module.set_table_section(self)

            if location in TABLE_PART[self.type]['transformer_locations']:
                # If placement is on a transformer location, update neighbors
                self.handle_transformer_neighbor(module, location)

        else:
            log("Unknown location {0} on {1}".format(location, self))

    def remove_module(self, module):
        module_flows = self.get_flows(ModuleFlowSegment)
        [mf.set_module(None) for mf in module_flows if mf.get_module() is module]


    def handle_transformer_neighbor(self, module, location):
        """
        When a module is placed on a transformerlocation, the neighbors will
        need an update. This function is called in place_module.
        """
        side = TABLE_PART[self.type]['transformer_locations'][location]
        if isinstance(module, ConnectionModule):
            # New possible neighbor, check if linked transformer module is placed
            linked_transformer = module.get_linked_module()
            if linked_transformer.get_table_section():
                # Linked transformer is placed, link neighbors through this transformer
                neighbor = linked_transformer.get_table_section()
                # Set neighbor and update neighbor table with self
                self.temporary_neighbors[side] = linked_transformer
                self.neighbors[side] = neighbor
                neighbor.upgrade_neighbor(module, self)
            else:
                # Linked transformer is not placed, set linked transformer as temporary neighbor 
                self.temporary_neighbors[side] = linked_transformer
        else:
            # Neighbor gone for sure! placed module is not a transformer 
            self.remove_neighbor_connection(side=side, remove_temp=True)

    def set_neighbor(self, location, neighbor):
        if location not in TABLE_PART[self.type]['table_connections']:
            log('Unknown location {0} on table with type {1}'.format(location, self.type))
            return 

        side = TABLE_PART[self.type]['table_connections'][location]

        if neighbor is None:
            # neighbor disconnected
            self.remove_neighbor_connection(side=side, remove_temp=True)
        elif self in neighbor.get_neighbors(temporary=True).values():
            # self is already known at neighbor, set both tables connected
            self.neighbors[side] = neighbor
            neighbor.upgrade_neighbor(self, self)
        else:
            # else set neighbor as temporary neighbor till he receives a connect aswell
            self.temporary_neighbors[side] = neighbor

    def upgrade_neighbor(self, n, neighbor):
        """
        Promote a temporary neighbor to real neighbor
        """
        for key, value in self.temporary_neighbors.iteritems():
            if value == n:
                self.neighbors[key] = neighbor

    def remove_neighbor_connection(self, side=None, neighbor=None, remove_temp=False):
        """
        Disconnects neighbor by either side or Table Section, also removes self at neighbor
        """
        if side is not None:
            neighbor = self.neighbors[side]
            if neighbor is not None:
                if remove_temp:
                    self.temporary_neighbors[side] = None
                self.remove_neighbor_connection(neighbor=neighbor)
        elif neighbor is not None:
            update_neighbor = False
            for key, value in self.neighbors.iteritems():
                if value == neighbor:
                    self.neighbors[key] = None
                    if remove_temp:
                        self.temporary_neighbors[key] = None
                    # Remove connection at neighbor aswell
                    update_neighbor = True

            if update_neighbor:
                neighbor.remove_neighbor_connection(neighbor=self)

    def neighbor_same_voltage(self, neighbor, accept_error_voltage=False):
        """
        Returns true if neighbor on given side has same voltage
        """
        if neighbor is None:
            return False
        return neighbor.get_voltage() is self.voltage or (accept_error_voltage and neighbor.get_voltage() is Voltages.ERROR)

    def get_table_cluster(self, flatten=False):
        table_cluster = create_table_cluster(self, np_arr=False)
        if flatten:
            table_cluster = [x for row in table_cluster for x in row if isinstance(x, TableSection)]
        return table_cluster

    def get_all_vertical_table_sections(self, excluded=[], only_direct=False, neighbors=None, accept_error_voltage=False):
        """
        get list of all vertical neighbors
        """
        if neighbors is None:
            # First call
            if self in excluded:
                neighbors = []
            else:
                neighbors = [self]
        for tp in [self.neighbors[Side.NORTH], self.neighbors[Side.SOUTH]]:
            if self.neighbor_same_voltage(tp,accept_error_voltage=accept_error_voltage) and tp not in neighbors and tp is not excluded:
                neighbors.append(tp)
                if not only_direct:
                    neighbors += tp.get_all_vertical_table_sections(neighbors=neighbors, excluded=excluded, accept_error_voltage=accept_error_voltage)
        return list(set(neighbors))

    def get_preferred_network_voltage(self, table_sections):
        """
        Returns network voltage based on placed modules
        """
        preferred_voltage = Voltages.ERROR

        modules = []
        for tp in table_sections:
            modules += tp.get_placed_modules(DefaultModule)

        voltages = [m.get_voltage() for m in modules]
        
        preferred_voltage = get_most_common_voltage_from_list(voltages)
        return preferred_voltage

    def get_power(self, excluded_table_sections=None, split=False):
        """
        Get power of this table section and all sections behind it
        """
        if excluded_table_sections is None:
            excluded_table_sections = []
        vertical_neighbors = self.get_all_vertical_table_sections()
        consumption = 0
        production = 0
        for tp in vertical_neighbors:
            if tp in excluded_table_sections:
                continue
            else:
                excluded_table_sections.append(tp)
            tp_consumption, tp_production = tp.get_table_section_power(excluded_table_sections=excluded_table_sections)
            consumption += tp_consumption
            production += tp_production
        if split:
            return consumption, abs(production)
        return consumption + production

    def get_table_section_power(self, excluded_table_sections):
        """
        Get power of this Table Section
        """
        module_power = [m.get_power() for m in self.get_placed_modules(DefaultModule, no_error_state=True)]
        transformer_modules = [m for m in self.get_placed_modules(ConnectionModule, no_error_state=True)]
        module_power += [m.get_power(only_if_lower_side=True, excluded_table_sections=excluded_table_sections) for m in transformer_modules]

        return (sum([x for x in module_power if x > 0]), sum([x for x in module_power if x < 0]))

    def update_voltage_by_transformer(self):
        """
        Set Table Section voltage based on placed transformer
        """
        t_modules = [m for m in self.get_placed_modules(ConnectionModule)]
        if len(t_modules) > 0:
            voltages = [m.get_voltage() for m in t_modules]
            
            v = get_most_common_voltage_from_list(voltages)
            self.set_voltage(v)
        elif False:
            # Future wire module
            pass
        else:
            self.set_voltage(Voltages.ERROR)

    def update_voltage_for_neighbors(self, table_sections_with_transformer):
        # Get all vertical neighbors (stop at neighbor with a transformer), including neighbors without voltage
        vertical_neighbors = self.get_all_vertical_table_sections(excluded=table_sections_with_transformer, accept_error_voltage=True)
        voltage = self.get_voltage()
        # set neighbor voltage same as this Table Sections voltage
        for neighbor in vertical_neighbors:
            if neighbor.get_voltage() is Voltages.ERROR:
                neighbor.set_voltage(voltage)

    def update_voltage(self):
        # set preferred voltage, also for neighbors
        vertical_neighbors = self.get_all_vertical_table_sections()
        v = self.get_preferred_network_voltage(vertical_neighbors)
        for neighbor in vertical_neighbors:
            neighbor.set_voltage(v)

    def update_module_flow_segments(self):
        flows = self.get_flows(ModuleFlowSegment)
        for flow in flows:
            flow.update_state()

    def update(self):
        # Connect Table Sections
        # Set direction based on production / consumption

        # Update each flow (speed / state / load)
        for f in self.flows:
            f.update()

        # Get all modules on this Table Section (plus connected parts on top/bottom)
        vertical_neighbors = self.get_all_vertical_table_sections() # This also includes self

        modules = []
        t_modules = []
        for tp in vertical_neighbors:
            modules += tp.get_placed_modules(DefaultModule, True)
            t_modules += tp.get_placed_modules(ConnectionModule, True)

        consumption, production = self.get_power(split=True)

        power_on_table = max(consumption, production)

        self.voltage_level = VoltageLevel.NORMAL # Set default voltage level
        # if there are at least 2 modules placed, of which 1 tranformer, activate flow
        if len(t_modules) > 0 and power_on_table is not 0:
            for tp in vertical_neighbors:
                tp.activate()

            # Update voltage level with power
            # UNCOMMENT TO ACTIVATE VOLTAGE LEVELS
#            self.voltage_level = GET_VOLTAGE_LEVEL(self.voltage, power_on_table)



        # set flows for table connections with load
        if self.voltage is not Voltages.ERROR:
            load = GET_LOAD(self.voltage, power_on_table)
            speed = GET_SPEED(power_on_table)
            direction = Direction.BACKWARDS if consumption < production else Direction.FORWARDS
            
            # Update rinf flow segments
            ring_flows = self.get_flows(RingFlowSegment)
            south_connected = self.neighbor_same_voltage(self.neighbors[Side.SOUTH])
            north_connected = self.neighbor_same_voltage(self.neighbors[Side.NORTH])

            for flow in ring_flows:
                # Update direction
                flow.set_direction(direction)
                flow.set_load(load)
                flow.set_speed(speed)
                flow.side_connected(Side.SOUTH, south_connected)
                flow.side_connected(Side.NORTH, north_connected)


    def activate(self):
        for f in self.flows:
            f.activate()

    def get_header_byte(self):
        # Header byte, divided in bits
        # | 7 6     | 5 4           | 3 2 1 0 |
        # | Voltage | Voltage level | Unused    |
        voltage = self.voltage if self.voltage is not Voltages.ERROR else 0
        voltage = voltage << 6
        voltage_level = self.voltage_level << 4
        byte = hexify(voltage ^ voltage_level)
        return [byte]

    def get_flow_bytes(self):
        # Get header byte and byte array
        header_byte = self.get_header_byte()
        flow_byte_array = []
        for f in self.flows: 
            flow_byte_array += f.get_byte() 
        return header_byte + flow_byte_array

    def __repr__(self):
        return 'Table section {0} ({1} voltage)'.format(self.id, self.get_voltage(True))
