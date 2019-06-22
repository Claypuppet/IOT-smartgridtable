
class MessageTypes:
    TABLE_CONNECTED, MODULE_PLACED, NEIGHBOR_CHANGED, CONFIG_CHANGED, \
    	COLOR_CHANGED, FLOW_CONFIG, FLOW_DISABLED, TIME_SYNC, RESET_TABLES, \
    	BUZZER_ENABLE, POWER_BOUNDARIES_CHANGED, SHUTDOWN_APP = range(12)


class SmartMessage(object):
    def __init__(self, type, args=None):
        self.args = args 
        self.type = type

    def __repr__(self):
        return "type: {0}, args: {1}".format(self.type, self.args)