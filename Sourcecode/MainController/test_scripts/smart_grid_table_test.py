import collections

from smart_grid_table import *
from values_for_testing import *
from logger import log



def start_tests():
    """
    Run all tests in this file
    """
    
    # Test module placements
    test_module_placement()
    # Test table neighbor placement
    test_neighbor_placement()
    # Test voltages algorithm
    test_voltage_algorithm()
    # Test load algorithm
    test_load_algorithm()
    
    log("\n    All tests success, table management ready for use\n")


def test_module_placement():
    """
    Test module placement
    """

    def get_modules(table_section):
        # Returns a list of module ids placed on table section
        return [m.get_id() for m in table_section.get_placed_modules()]

    # Create table (also creates modules)
    table = SmartGridTable()

    # Connect a table (table_id, child_id, table_type)
    table.table_connected(table_1_id, None, table_type)
    table_section1 = table.get_table_section(table_1_id)

    # Place modules on Table Section (table_id, location_id, module_id) and check if module is placed
    table.module_placed(table_1_id, module_location_west, module_medium)
    assert collections.Counter(get_modules(table_section1)) == collections.Counter([module_medium])

    table.module_placed(table_1_id, module_location_east, module_medium)
    assert collections.Counter(get_modules(table_section1)) == collections.Counter([module_medium])

    table.module_placed(table_1_id, module_location_east, None)
    assert collections.Counter(get_modules(table_section1)) == collections.Counter([])

    table.module_placed(table_1_id, module_location_west, module_low)
    assert collections.Counter(get_modules(table_section1)) == collections.Counter([module_low])

    table.module_placed(table_1_id, module_location_northwest, module_low2)
    assert collections.Counter(get_modules(table_section1)) == collections.Counter([module_low, module_low2])

    table.module_placed(table_1_id, module_location_northeast, module_low3)
    assert collections.Counter(get_modules(table_section1)) == collections.Counter([module_low, module_low2, module_low3])

    table.module_placed(table_1_id, module_location_east, transformer_high)
    assert collections.Counter(get_modules(table_section1)) == collections.Counter([module_low, module_low2, module_low3, transformer_high])

    table.module_placed(table_1_id, module_location_southeast, module_medium2)
    assert collections.Counter(get_modules(table_section1)) == collections.Counter([module_low, module_low2, module_low3, transformer_high, module_medium2])

    table.module_placed(table_1_id, module_location_southwest, module_high)
    assert collections.Counter(get_modules(table_section1)) == collections.Counter([module_low, module_low2, module_low3, transformer_high, module_medium2, module_high])


def test_neighbor_placement():
    """
    Test neighbor placement and cluster forming
    """

    # Create table (also creates modules)
    table = SmartGridTable()

    # Connect a table (table_id, child_id, table_type)
    table.table_connected(table_1_id, None, table_type)
    table.table_connected(table_2_id, None, table_type)
    table.table_connected(table_3_id, None, table_type)

    # Get Table Section 1 and 2
    table_section1 = table.get_table_section(table_1_id)
    table_section2 = table.get_table_section(table_2_id)
    table_section3 = table.get_table_section(table_3_id)

    # connect neighbor. table_neighbor_changed(table_id, location_id, connected_neighbor_id)
    table.table_neighbor_changed(table_1_id, table_conn_point_north, table_2_conn_south)
    table.table_neighbor_changed(table_2_id, table_conn_point_south, table_1_conn_north)
    assert table_section1.get_neighbors()[Side.NORTH] is table_section2
    assert table_section2.get_neighbors()[Side.SOUTH] is table_section1
    assert collections.Counter(table_section1.get_table_cluster(flatten=True)) == collections.Counter([table_section1, table_section2])
    assert collections.Counter(table_section2.get_table_cluster(flatten=True)) == collections.Counter([table_section1, table_section2])

    # remove neighbor connection
    table.table_neighbor_changed(table_1_id, table_conn_point_north, None)
    assert table_section1.get_neighbors()[Side.NORTH] is None
    assert table_section2.get_neighbors()[Side.SOUTH] is None
    assert collections.Counter(table_section1.get_table_cluster(flatten=True)) == collections.Counter([table_section1])
    assert collections.Counter(table_section2.get_table_cluster(flatten=True)) == collections.Counter([table_section2])
    
    table.table_neighbor_changed(table_2_id, table_conn_point_south, None)
    assert table_section1.get_neighbors()[Side.NORTH] is None
    assert table_section2.get_neighbors()[Side.SOUTH] is None

    # connect by transformers. module_placed(table_id, location_id, module_id)
    table.module_placed(table_3_id, module_location_east, transformer_high) # Place transformer high
    table.module_placed(table_2_id, module_location_west, transformer_mediumH) # Place transformer medium
    assert table_section2.get_neighbors()[Side.WEST] is table_section3
    assert table_section3.get_neighbors()[Side.EAST] is table_section2
    assert collections.Counter(table_section2.get_table_cluster(flatten=True)) == collections.Counter([table_section3, table_section2])
    assert collections.Counter(table_section3.get_table_cluster(flatten=True)) == collections.Counter([table_section3, table_section2])

    table.module_placed(table_2_id, module_location_west, None) # Remove transformer medium
    assert table_section2.get_neighbors()[Side.SOUTH] is None
    assert table_section3.get_neighbors()[Side.NORTH] is None

    table.table_neighbor_changed(table_1_id, table_conn_point_north, table_2_conn_south)
    table.table_neighbor_changed(table_2_id, table_conn_point_south, table_1_conn_north) #
    table.module_placed(table_2_id, module_location_west, transformer_mediumH) # Place transformer medium
    assert table_section1.get_neighbors()[Side.NORTH] is table_section2
    assert table_section2.get_neighbors()[Side.SOUTH] is table_section1
    assert table_section2.get_neighbors()[Side.WEST] is table_section3
    assert table_section3.get_neighbors()[Side.EAST] is table_section2
    assert collections.Counter(table_section1.get_table_cluster(flatten=True)) == collections.Counter([table_section1, table_section2, table_section3])
    assert collections.Counter(table_section2.get_table_cluster(flatten=True)) == collections.Counter([table_section1, table_section2, table_section3])
    assert collections.Counter(table_section3.get_table_cluster(flatten=True)) == collections.Counter([table_section1, table_section2, table_section3])


def test_voltage_algorithm():
    """
    Testing voltage algorithm over multiple tables
    """

    # Create table (also creates modules)
    table = SmartGridTable()

    # Connect a table (table_id, child_id, table_type)
    table.table_connected(table_1_id, None, table_type)
    table.table_connected(table_2_id, None, table_type)
    table.table_connected(table_3_id, None, table_type)

    # Get Table Sections
    table_section1 = table.get_table_section(table_1_id)
    table_section2 = table.get_table_section(table_2_id)
    table_section3 = table.get_table_section(table_3_id)

    # connect neighbor. table_neighbor_changed(table_id, location_id, connected_neighbor_id)
    table.table_neighbor_changed(table_1_id, table_conn_point_north, table_2_conn_south)
    table.table_neighbor_changed(table_2_id, table_conn_point_south, table_1_conn_north)
    
    table.get_flow_configurations()
    assert table_section1.get_voltage() is Voltages.ERROR, 'Voltage is {0}, should be ERROR'.format(table_section1.get_voltage(string=True))
    assert table_section2.get_voltage() is Voltages.ERROR, 'Voltage is {0}, should be ERROR'.format(table_section2.get_voltage(string=True))
    assert table_section3.get_voltage() is Voltages.ERROR, 'Voltage is {0}, should be ERROR'.format(table_section3.get_voltage(string=True))

    # connect by transformers. module_placed(table_id, location_id, module_id)
    table.module_placed(table_3_id, module_location_east, transformer_high) # Place transformer high
    table.module_placed(table_2_id, module_location_west, transformer_mediumH) # Place transformer medium

    table.get_flow_configurations()
    assert table_section1.get_voltage() is Voltages.MEDIUM, 'Voltage is {0}, should be MEDIUM'.format(table_section1.get_voltage(string=True))
    assert table_section2.get_voltage() is Voltages.MEDIUM, 'Voltage is {0}, should be MEDIUM'.format(table_section2.get_voltage(string=True))
    assert table_section3.get_voltage() is Voltages.HIGH, 'Voltage is {0}, should be HIGH'.format(table_section3.get_voltage(string=True))

    table.module_placed(table_1_id, module_location_east, transformer_low) # Place transformer low

    table.get_flow_configurations()
    assert table_section1.get_voltage() is Voltages.LOW, 'Voltage is {0}, should be LOW'.format(table_section1.get_voltage(string=True))
    assert table_section2.get_voltage() is Voltages.MEDIUM, 'Voltage is {0}, should be MEDIUM'.format(table_section2.get_voltage(string=True))
    assert table_section3.get_voltage() is Voltages.HIGH, 'Voltage is {0}, should be HIGH'.format(table_section3.get_voltage(string=True))

    # Remove all modules and connect 2-3 vertical
    table.module_placed(table_3_id, module_location_east, None) # Remove transformer high
    table.module_placed(table_2_id, module_location_west, None) # Remove transformer medium
    table.module_placed(table_1_id, module_location_east, None) # Remove transformer low
    table.table_neighbor_changed(table_3_id, table_conn_point_south, table_2_conn_north)
    table.table_neighbor_changed(table_2_id, table_conn_point_north, table_3_conn_south)

    table.get_flow_configurations()
    assert table_section1.get_voltage() is Voltages.ERROR, 'Voltage is {0}, should be ERROR'.format(table_section1.get_voltage(string=True))
    assert table_section2.get_voltage() is Voltages.ERROR, 'Voltage is {0}, should be ERROR'.format(table_section2.get_voltage(string=True))
    assert table_section3.get_voltage() is Voltages.ERROR, 'Voltage is {0}, should be ERROR'.format(table_section3.get_voltage(string=True))

    table.module_placed(table_3_id, module_location_east, module_high) # Place module high

    table.get_flow_configurations()
    assert table_section1.get_voltage() is Voltages.HIGH, 'Voltage is {0}, should be HIGH'.format(table_section1.get_voltage(string=True))
    assert table_section2.get_voltage() is Voltages.HIGH, 'Voltage is {0}, should be HIGH'.format(table_section2.get_voltage(string=True))
    assert table_section3.get_voltage() is Voltages.HIGH, 'Voltage is {0}, should be HIGH'.format(table_section3.get_voltage(string=True))

    table.module_placed(table_2_id, module_location_southwest, module_medium) # Place module medium

    table.get_flow_configurations()
    assert table_section1.get_voltage() is Voltages.MEDIUM, 'Voltage is {0}, should be MEDIUM'.format(table_section1.get_voltage(string=True))
    assert table_section2.get_voltage() is Voltages.MEDIUM, 'Voltage is {0}, should be MEDIUM'.format(table_section2.get_voltage(string=True))
    assert table_section3.get_voltage() is Voltages.MEDIUM, 'Voltage is {0}, should be MEDIUM'.format(table_section3.get_voltage(string=True))

    table.module_placed(table_2_id, module_location_southeast, module_low) # Place module low

    table.get_flow_configurations()
    assert table_section1.get_voltage() is Voltages.LOW, 'Voltage is {0}, should be LOW'.format(table_section1.get_voltage(string=True))
    assert table_section2.get_voltage() is Voltages.LOW, 'Voltage is {0}, should be LOW'.format(table_section2.get_voltage(string=True))
    assert table_section3.get_voltage() is Voltages.LOW, 'Voltage is {0}, should be LOW'.format(table_section3.get_voltage(string=True))

    table.module_placed(table_1_id, module_location_west, module_medium) # Place module medium

    table.get_flow_configurations()
    assert table_section1.get_voltage() is Voltages.MEDIUM, 'Voltage is {0}, should be MEDIUM'.format(table_section1.get_voltage(string=True))
    assert table_section2.get_voltage() is Voltages.MEDIUM, 'Voltage is {0}, should be MEDIUM'.format(table_section2.get_voltage(string=True))
    assert table_section3.get_voltage() is Voltages.MEDIUM, 'Voltage is {0}, should be MEDIUM'.format(table_section3.get_voltage(string=True))

    table.module_placed(table_3_id, module_location_west, transformer_high) # Place transformer high
    
    table.get_flow_configurations()
    assert table_section1.get_voltage() is Voltages.HIGH, 'Voltage is {0}, should be HIGH'.format(table_section1.get_voltage(string=True))
    assert table_section2.get_voltage() is Voltages.HIGH, 'Voltage is {0}, should be HIGH'.format(table_section2.get_voltage(string=True))
    assert table_section3.get_voltage() is Voltages.HIGH, 'Voltage is {0}, should be HIGH'.format(table_section3.get_voltage(string=True))

    table.module_placed(table_1_id, module_location_west, transformer_mediumH) # Place transformer medium

    table.get_flow_configurations()
    assert table_section1.get_voltage() is Voltages.MEDIUM, 'Voltage is {0}, should be MEDIUM'.format(table_section1.get_voltage(string=True))
    assert table_section2.get_voltage() is Voltages.MEDIUM, 'Voltage is {0}, should be MEDIUM'.format(table_section2.get_voltage(string=True))
    assert table_section3.get_voltage() is Voltages.HIGH, 'Voltage is {0}, should be HIGH'.format(table_section3.get_voltage(string=True))

    table.module_placed(table_3_id, module_location_west, transformer_low) # Place transformer low
    
    table.get_flow_configurations()
    assert table_section1.get_voltage() is Voltages.MEDIUM, 'Voltage is {0}, should be MEDIUM'.format(table_section1.get_voltage(string=True))
    assert table_section2.get_voltage() is Voltages.LOW, 'Voltage is {0}, should be LOW'.format(table_section2.get_voltage(string=True))
    assert table_section3.get_voltage() is Voltages.LOW, 'Voltage is {0}, should be LOW'.format(table_section3.get_voltage(string=True))

    table.table_neighbor_changed(table_3_id, table_conn_point_south, None)
    table.table_neighbor_changed(table_2_id, table_conn_point_north, None)

    table.get_flow_configurations()
    assert table_section1.get_voltage() is Voltages.MEDIUM, 'Voltage is {0}, should be MEDIUM'.format(table_section1.get_voltage(string=True))
    assert table_section2.get_voltage() is Voltages.MEDIUM, 'Voltage is {0}, should be MEDIUM'.format(table_section2.get_voltage(string=True))
    assert table_section3.get_voltage() is Voltages.LOW, 'Voltage is {0}, should be LOW'.format(table_section3.get_voltage(string=True))


def test_load_algorithm():
    """
    Test loads
    """

    def get_power(*objs):
        return sum([int(obj.get_power()) for obj in objs])

    # Create table (also creates modules)
    table = SmartGridTable()

    # Change config, module_config_changed(self, module_id, config_id, value)
    table.module_config_changed(module_medium2, 5, 50)   # 50 prod
    table.module_config_changed(module_medium2, 7, 0)    # 0 cons
    table.module_config_changed(module_low, 2, 20)       # 20 cons
    table.module_config_changed(module_low, 6, 0)        # 0 prod
    table.module_config_changed(module_low2, 2, 0)       # 0 cons
    table.module_config_changed(module_low2, 6, 50)      # 50 prod

    # Connect a table (table_id, child_id, table_type)
    table.table_connected(table_1_id, None, table_type)
    table.table_connected(table_2_id, None, table_type)
    table.table_connected(table_3_id, None, table_type)
    table.table_connected(table_4_id, None, table_type)

    # Get Table Sections
    table_section1 = table.get_table_section(table_1_id)
    table_section2 = table.get_table_section(table_2_id)
    table_section3 = table.get_table_section(table_3_id)
    table_section4 = table.get_table_section(table_4_id)

    # connect by transformers. module_placed(table_id, location_id, module_id)
    table.module_placed(table_1_id, module_location_east, transformer_mediumL) # Place transformer high
    table.module_placed(table_2_id, module_location_west, transformer_low) # Place transformer medium

    table.get_flow_configurations()
    assert get_power(table_section1) == 0
    assert get_power(table_section2) == 0
    assert get_power(table_section3) == 0

    table.module_placed(table_2_id, module_location_northwest, module_low) # Place low module

    table.get_flow_configurations()
    assert get_power(table_section1) == get_power(table.get_module(module_low))
    assert get_power(table_section2) == get_power(table.get_module(module_low))
    assert get_power(table.get_module(transformer_mediumL)) == get_power(table.get_module(module_low))
    assert get_power(table.get_module(transformer_low)) == get_power(table.get_module(module_low)) * -1

    table.module_placed(table_1_id, module_location_northwest, module_medium2) # Place medium module

    table.get_flow_configurations()
    assert get_power(table_section1) == get_power(table.get_module(module_low), table.get_module(module_medium2))
    assert get_power(table_section2) == get_power(table.get_module(module_low))
    assert get_power(table.get_module(transformer_mediumL)) == get_power(table.get_module(module_low))
    assert get_power(table.get_module(transformer_low)) == get_power(table.get_module(module_low)) * -1

    table.module_placed(table_1_id, module_location_southwest, module_high) # Place high (misplaced) module

    table.get_flow_configurations()
    assert get_power(table_section1) == get_power(table.get_module(module_low), table.get_module(module_medium2))
    assert get_power(table_section2) == get_power(table.get_module(module_low))
    assert get_power(table.get_module(transformer_mediumL)) == get_power(table.get_module(module_low))
    assert get_power(table.get_module(transformer_low)) == get_power(table.get_module(module_low)) * -1

    table.module_placed(table_2_id, module_location_east, wire_low) # Place wire
    table.module_placed(table_3_id, module_location_west, wire_low2) # Place wire

    table.get_flow_configurations()
    assert get_power(table_section1) == get_power(table.get_module(module_low), table.get_module(module_medium2))
    assert get_power(table_section2) == get_power(table.get_module(module_low))
    assert get_power(table_section3) == 0
    assert get_power(table.get_module(transformer_mediumL)) == get_power(table.get_module(module_low))
    assert get_power(table.get_module(transformer_low)) == get_power(table.get_module(module_low)) * -1
    assert get_power(table.get_module(wire_low)) == 0
    assert get_power(table.get_module(wire_low2)) == 0

    table.module_placed(table_3_id, module_location_northwest, module_low2) # Place low module 2

    table.get_flow_configurations()
    assert get_power(table_section1) == get_power(table.get_module(module_low), table.get_module(module_low2), table.get_module(module_medium2))
    assert get_power(table_section2) == get_power(table.get_module(module_low), table.get_module(module_low2))
    assert get_power(table_section3) == get_power(table.get_module(module_low2))
    assert get_power(table.get_module(transformer_mediumL)) == get_power(table.get_module(module_low), table.get_module(module_low2))
    assert get_power(table.get_module(transformer_low)) == get_power(table.get_module(module_low), table.get_module(module_low2)) * -1
    assert get_power(table.get_module(wire_low)) == get_power(table.get_module(module_low2))
    assert get_power(table.get_module(wire_low2)) == get_power(table.get_module(module_low2)) * -1