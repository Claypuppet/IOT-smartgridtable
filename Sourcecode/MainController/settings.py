"""
Debugging
"""

DEBUG = True

"""
Time configuration in seconds
"""
CONFIG_SEND_DELAY = 0.2

SYNC_DELAY = 20

"""
Buzzer config
"""

BUZZ_DURATION = 0.1

BUZZ_SLEEP = 0.1

BUZZ_AMOUNT_OK = 1

BUZZ_AMOUNT_ERROR = 3

"""
Module configuration file location
"""
MODULE_CONFIG_FILE = 'config/moduleConfig.json'
TABLE_CONFIG_FILE = 'config/tableConfig.json'

BG_COLOR = (0, .0, .2, 1)

"""
Colors used in application
"""
COLOR_DICT = {
    "vlow": {
        "id": 0,
        "name": "low voltage",
        "color": (0.1, 0.8, 1.0, 1.0) # white-ish
    },
    "vmedium": {
        "id": 1,
        "name": "medium voltage",
        "color": (0.6, 0.3, 1.0, 1.0) # light purple
    },
    "vhigh": {
        "id": 2,
        "name": "high voltage",
        "color": (0.2, 0.1, 1.0, 1.0) # Dark blue
    },
    "lnormal": {
        "id": 3,
        "name": "normal load",
        "color": (0, 1, 0, 1),  # Green
    },
    "lhigh": {
        "id": 4,
        "name": "high load",
        "color": (1, 1, 0, 1),  # Yellow
    },
    "lcritical": {
        "id": 5,
        "name": "critical load",
        "color": (1, 0, 0, 1)   # Red
    }
}

"""
Enums
"""

# Grid voltages

class VoltageLevel:
    # TODO: Up to 4 voltage levels
    NORMAL, HIGH, CRITICAL, UNSTABLE = range(4)

class Voltages:
    ERROR, LOW, MEDIUM, HIGH = range(-1, 3)

    @staticmethod
    def enum_to_color(e):
        if e is Voltages.ERROR:
            return (1.0, .0, .0, 1.0)
        elif e is Voltages.LOW:
            return COLOR_DICT["vlow"]["color"]
        elif e is Voltages.MEDIUM:
            return COLOR_DICT["vmedium"]["color"]
        elif e is Voltages.HIGH:
            return COLOR_DICT["vhigh"]["color"]
        raise Exception('Cannot convert this to color')

    @staticmethod
    def enum_to_flow_color(e):
        if e is Voltages.ERROR:
            return (1, 1, 1, 1)
        elif e is Voltages.LOW:
            return COLOR_DICT["vlow"]["color"]
        elif e is Voltages.MEDIUM:
            return COLOR_DICT["vmedium"]["color"]
        elif e is Voltages.HIGH:
            return COLOR_DICT["vhigh"]["color"]
        raise Exception('Cannot convert this to color')

    @staticmethod
    def str_to_enum(s):
        if s == "error":
            return Voltages.ERROR
        elif s == "low":
            return Voltages.LOW
        elif s == "medium":
            return Voltages.MEDIUM
        elif s == "high":
            return Voltages.HIGH
        raise Exception('Cannot convert this to enum')

    @staticmethod
    def enum_to_str(e):
        if e is Voltages.ERROR:
            return "Error"
        elif e is Voltages.LOW:
            return "Low"
        elif e is Voltages.MEDIUM:
            return "Medium"
        elif e is Voltages.HIGH:
            return "High"
        raise Exception('Cannot convert this to string')


class Roles:
    PRODUCTION, CONSUMPTION = range(2)

    @staticmethod
    def str_to_enum(s):
        if s == "production":
            return Roles.PRODUCTION
        elif s == "consumption":
            return Roles.CONSUMPTION
        raise Exception('Cannot convert this to enum')

    @staticmethod
    def enum_to_str(e):
        if e == Roles.PRODUCTION:
            return "production"
        elif e == Roles.CONSUMPTION:
            return "consumption"
        raise Exception('Cannot convert this to enum')


# FlowSegment speed
class Speed:
    # Can be expanded to up to 8 speed levels
    NORMAL, FAST, FASTER, FASTEST = range(4)

# FlowSegment direction
class Direction:
    FORWARDS, BACKWARDS = range(2)

# FlowSegment load
class Load:
    NORMAL, HIGH, CRITICAL = range(3)

# Sides, used in Table Section detection
class Side:
    NORTH, EAST, SOUTH, WEST = range(4)

    @staticmethod
    def flip_side(s):
        if s == Side.SOUTH:
            return Side.NORTH
        elif s == Side.WEST:
            return Side.EAST
        elif s == Side.NORTH:
            return Side.SOUTH
        elif s == Side.EAST:
            return Side.WEST

    @staticmethod
    def str_to_enum(s):
        if s == "north":
            return Side.NORTH
        elif s == "east":
            return Side.EAST
        elif s == "south":
            return Side.SOUTH
        elif s == "west":
            return Side.WEST
        raise Exception('Cannot convert this to enum')

    @staticmethod
    def enum_to_str(e):
        if e == Side.NORTH:
            return "north"
        elif e == Side.EAST:
            return "east"
        elif e == Side.SOUTH:
            return "south"
        elif e == Side.WEST:
            return "west"
        raise Exception('Cannot convert this to string')

# FlowSegment state
class State:
    OFF, ERROR, PASSIVE, ACTIVE = range(4)

"""
Boundaries
"""
POWER_SPEED_BOUNDARIES = {
    Speed.NORMAL: 150,
    Speed.FAST: 300,
    Speed.FASTER: 400
}

VOLTAGE_POWER_LOAD_BOUNDARIES = {
    Voltages.LOW: {
        Load.CRITICAL: 300,     # capacity, power > capacity -> critical load 
        Load.HIGH: .75          # high modifier, power > capacity * high modifier -> high load
    },
    Voltages.MEDIUM: {
        Load.CRITICAL: 500,     # capacity, critical load 
        Load.HIGH: .80          # x% of capacity, high load
    },
    Voltages.HIGH: {
        Load.CRITICAL: 1300,     # capacity, critical load 
        Load.HIGH: .90          # x% of capacity, high load
    }
}

VOLTAGE_LEVEL_BOUNDARIES = {
    Voltages.LOW: 400,
    Voltages.MEDIUM: 800,
    Voltages.HIGH: 1800
}

"""
Helper functions
"""

def GET_LOAD(voltage, power):
    if voltage is Voltages.ERROR:
        return Load.NORMAL

    power = abs(power)
    high_mod = VOLTAGE_POWER_LOAD_BOUNDARIES[voltage][Load.HIGH]
    capacity = VOLTAGE_POWER_LOAD_BOUNDARIES[voltage][Load.CRITICAL]
    if power <= high_mod * capacity:
        return Load.NORMAL
    elif power <= capacity:
        return Load.HIGH
    else:
        return Load.CRITICAL


def GET_SPEED(power):
    power = abs(power)
    if power <= POWER_SPEED_BOUNDARIES[Speed.NORMAL]:
        return Speed.NORMAL
    elif power <= POWER_SPEED_BOUNDARIES[Speed.FAST]:
        return Speed.FAST
    elif power <= POWER_SPEED_BOUNDARIES[Speed.FASTER]:
        return Speed.FASTER
    else: 
        return Speed.FASTEST

def GET_VOLTAGE_LEVEL(voltage, power):
    if voltage is Voltages.ERROR:
        return VoltageLevel.NORMAL

    power = abs(power)
    if power > VOLTAGE_LEVEL_BOUNDARIES[voltage]:
        return VoltageLevel.UNSTABLE 
    else: # TODO: multiple boundaries checks
        return VoltageLevel.CRITICAL




"""
Table Section settings, per type.
example: x in TABLE_PART[type]['module_locations']
"""
TABLE_PART = {
    1: {
        'module_locations': [0,1,2,3,4,5],
        'transformer_locations': {
            0:      Side.WEST,
            3:      Side.EAST
        },
        'table_connections': {
            0:      Side.NORTH,
            1:      Side.SOUTH
        }
    },
    255: {
        'module_locations': [1],
        'transformer_locations': []
    },
    254: {
        'module_locations': [1,2,3,4,5,6],
        'transformer_locations': []
    },
    253: {
        'module_locations': [1,2,3,4,5,6],
        'transformer_locations': {
            1:      Side.WEST,
            4:      Side.EAST
        }
    }
}