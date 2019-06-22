from settings import *
from module import Module, DefaultModule, ConnectionModule, TransformerModule, WireModule, ImportExportModule
from logger import log
from hexifier import hexify

class FlowSegment(object):
    """
    Abstract flow segment object
    """
    def __init__(self):
        super(FlowSegment, self).__init__()
        self.voltage = Voltages.LOW         # FlowSegment voltage
        self.load = Load.NORMAL             # FlowSegment load
        self.speed = Speed.NORMAL           # FlowSegment speed
        self.direction = Direction.FORWARDS # FlowSegment direction
        self.state = State.OFF              # FlowSegment state

    def set_voltage(self, voltage):
        if voltage is Voltages.ERROR:
            # If voltage is error, the flow is turned off
            self.state = State.OFF
        else:
            self.voltage = voltage
            self.state = State.PASSIVE
            if isinstance(self, ModuleFlowSegment):
                self.update_state()

    def set_load(self, load):
        self.load = load

    def set_speed(self, speed):
        self.speed = speed

    def set_direction(self, direction):
        self.direction = direction

    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def get_voltage(self):
        return self.voltage

    def get_load(self):
        return self.load

    def get_direction(self):
        return self.direction

    def get_speed(self):
        return self.speed

    def activate(self):
        """
        Activates the flow if it is passive
        """
        if self.state is State.PASSIVE:
            self.state = State.ACTIVE

    def get_byte(self):
        # Flow byte, divided in bits
        # | 7 6 5 | 4         | 3 2  | 1 0   |
        # | Speed | direction | load | state |
        speed = self.speed << 5
        direction = self.direction << 4
        load = self.load << 2
        state = self.state
        byte = hexify(speed ^ direction ^ load ^ state)
        return [byte]

    def __repr__(self):
        return 'FlowSegment [s {0},v {1},l {2}]'.format(self.state, self.voltage, self.load)


class ModuleFlowSegment(FlowSegment):
    """
    Flow segment connected to a module
    """
    def __init__(self):
        super(ModuleFlowSegment, self).__init__()
        self.module = None # Module connected to module flow segment

    def update_direction(self):
        if self.module is None:
            self.direction = Direction.FORWARDS
        elif self.module.get_power() > 0:
            self.direction = Direction.FORWARDS
        else:
            self.direction = Direction.BACKWARDS

    def update_speed(self):
        if self.module is None:
            self.speed = Speed.NORMAL
            return
        power = self.module.get_power()
        self.speed = GET_SPEED(power)

    def update_load(self):
        if self.module is None:
            self.speed = Speed.NORMAL
            return
        power = self.module.get_power()
        self.load =GET_LOAD(self.voltage, power)


    def update_state(self):
        if isinstance(self.module, ConnectionModule):
            self.state = State.ERROR
        elif self.module is not None:
            self.state = State.PASSIVE if self.voltage is self.module.get_voltage() else State.ERROR
        else:
            self.state = State.OFF

    def update(self):
        self.update_state()
        if self.state is State.ERROR:
            return
        self.update_direction()
        self.update_speed()
        self.update_load()

    def set_module(self, module):
        if module is None and self.module is not None:
            self.module.set_table_section(None)
        self.module = module

    def get_module(self, no_error_state=True):
        if not no_error_state or self.state is not State.ERROR:
            return self.module

    def activate(self):
        """
        Activates the flow if it is passive, and at least consuming or producing
        """
        if self.state is State.PASSIVE and self.module is not None:
            if self.module.get_power() != 0.0:
                self.state = State.ACTIVE

    def __repr__(self):
        return 'Default FlowSegment [s {0},v {1}] (module: {2})'.format(self.state, self.voltage, self.module)


class ConnectionModuleFlowSegment(ModuleFlowSegment):
    def __init__(self):
        super(ConnectionModuleFlowSegment, self).__init__()

    def update_state(self):
        if self.module is not None:
            self.state = State.PASSIVE if self.voltage is self.module.get_voltage() else State.ERROR
        else:
            self.state = State.OFF

    def get_byte(self):
        # Default off
        byte1 = byte2 = hexify(State.OFF)

        if isinstance(self.module, DefaultModule):
            byte2 = super(ConnectionModuleFlowSegment, self).get_byte()[0]


        else:
            speed = self.speed << 5
            direction = self.direction << 4
            load = self.load << 2
            state = self.state
            if self.voltage is Voltages.HIGH:
                byte1 = hexify(speed ^ direction ^ load ^ state)
            else:
                byte2 = hexify(speed ^ direction ^ load ^ state)

        return [byte1, byte2, byte1]

    def __repr__(self):
        return 'Transformer FlowSegment [s {0},v {1}] (module: {2})'.format(self.state, self.voltage, self.module)

class RingFlowSegment(FlowSegment):
    def __init__(self, side=None):
        super(RingFlowSegment, self).__init__()
        self.side = side
        self.force_disabled = False 

    def side_connected(self, side, connected):
        """
        If Table Section is connected on side, disable state
        """
        if self.side is side and connected is True:
            self.state = State.OFF

    def set_force_disabled(self, disabled):
        self.force_disabled = disabled

    def update(self):
        if self.force_disabled:
            self.state = State.OFF


class NeighborFlowSegment(RingFlowSegment):
    def __init__(self, side):
        super(NeighborFlowSegment, self).__init__(side)

    def side_connected(self, side, connected):
        """
        If Table Section is not connected on side, disable state
        """
        if self.side is side and connected is False:
            self.state = State.OFF

