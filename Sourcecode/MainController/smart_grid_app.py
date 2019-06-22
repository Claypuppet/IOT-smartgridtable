import sys
import time

from logger import log
from settings import *

from daemon_threads import *
from smart_grid_messaging import *
from smart_grid_table import SmartGridTable
from mysensors_gateway_connector import GatewayConnector, MySenTypes, MySenCommands
from gui import Gui
from flask_api import ApiServer

from buzzer import Buzzer


class SmartGridApp(object):
    """
    SmartGridApp, the point in the application where everything comes together
    """
    
    def __init__(self, serial_port, baudrate):
        # App start moment in millis
        self.start_time = int(round(time.time() * 1000))

        # Create smart grid table
        self.smart_grid_table = SmartGridTable()

        # Create buzzer
        self.buzzer = Buzzer()

        # Message buffer
        self.message_buffer = []

        # Define message functions
        self.message_functions = {
            MessageTypes.TABLE_CONNECTED: self.table_connected,
            MessageTypes.MODULE_PLACED: self.module_placed,
            MessageTypes.NEIGHBOR_CHANGED: self.table_neighbor_changed,
            MessageTypes.CONFIG_CHANGED: self.module_config_changed,
            MessageTypes.FLOW_DISABLED: self.flow_disabled,
            MessageTypes.FLOW_CONFIG: self.send_flow_config,
            MessageTypes.COLOR_CHANGED: self.send_flow_color,
            MessageTypes.TIME_SYNC: self.send_time_sync,
            MessageTypes.RESET_TABLES: self.reset_table_sections,
            MessageTypes.BUZZER_ENABLE: self.buzzer_enabled,
            MessageTypes.POWER_BOUNDARIES_CHANGED: self.power_boundaries_changed,
            MessageTypes.SHUTDOWN_APP: self.shutdown_app
        }

        # Define send config and time sync timers
        self.send_flow_config_timer = start_daemon_timer(0, None, start=False)
        self.time_sync_timer = start_daemon_timer(SYNC_DELAY, self.need_time_sync_msg)


        # Create and start gateway connection (threaded)
        self.gateway_conn = GatewayConnector(self.add_message, serial_port, baudrate)
        start_daemon_thread(self.gateway_conn.start_serial_read, ())
        log('--------GW CONN STARTED')

        # Create and start flask server (threaded)
        self.api = ApiServer(self.smart_grid_table, self.add_message)
        start_daemon_thread(self.api.run, ())
        log('--------API STARTED')

        # Create and start GUI  (threaded)
        self.gui = Gui(self.smart_grid_table, self.add_message)
        start_daemon_thread(self.gui.run, ())
        log('--------GUI STARTED')


        log('--------RESETTING Table SectionS')
        self.need_reset_table_sections()

        # Start message handler in main thread
        log('--------START MESSAGE HANDLING')
        self.handle_messages()

    def add_message(self, message):
        """
        Add smart message to buffer
        """
        if isinstance(message, SmartMessage):
            self.message_buffer.append(message)

    def handle_messages(self):
        """
        Main thread loop for handling messages between different parts of the application
        """
        while 1:
            if len(self.message_buffer) is 0:
                time.sleep(0.02)
                continue

            message = self.message_buffer.pop(0)
            if message.type not in list(self.message_functions.keys()):
                continue

            if message.args is not None:
                self.message_functions[message.type](*message.args)
            else:
                self.message_functions[message.type]()

    def shutdown_app(self):
        """
        Shutdown application (and kill buzzer)
        """
        log('Shutdown application')
        self.buzzer.kill()
        sys.exit()

    def send_flow_config(self):
        """
        Get new flow config for each Table Section and send to serial connection
        """
        self.buzzer.buzz(BUZZ_AMOUNT_OK)
        self.update_gui()

        # get table flow config
        table_flow_configs = self.smart_grid_table.get_flow_configurations()
        for table_flow in table_flow_configs:
            # log('sending config to table', table_flow.get('id'))
            self.gateway_conn.send_serial_message(
                table_flow.get('destination'), table_flow.get('config'), 
                MySenCommands.STREAM, MySenTypes.V_VAR4)

    def send_time_sync(self):
        """
        Send main controller time (since startup) to each Table Section controller
        """
        self.time_sync_timer.cancel()
        self.time_sync_timer = start_daemon_timer(SYNC_DELAY, self.need_time_sync_msg)
        log('Time sync')

        time_since_startup = self.get_time_since_startup()

        # Send broadcast (255) with time since startup (in milliseconds)
        self.gateway_conn.send_serial_message(
            255, time_since_startup, MySenCommands.SET, MySenTypes.V_VAR5)

    def send_flow_color(self, color_type, color):
        """
        Send new voltage/load color to each Table Section controller
        """
        log('Flow color change... {0} will be color {1}'.format(color_type, color))

        # Send broadcast (255) with color (payload) and type (child_id)
        self.gateway_conn.send_serial_message(
            255, color, MySenCommands.SET, MySenTypes.V_RGB, child_id=color_type)

    def get_time_since_startup(self, string=False):
        millis = int(round(time.time() * 1000))
        since_startup = millis - self.start_time
        return str(since_startup) if string else since_startup

    def reset_table_sections(self):
        """
        Send reset message to all Table Sections
        """

        # Send broadcast (255) with reset message
        self.gateway_conn.send_serial_message(
            255, None, MySenCommands.SET, MySenTypes.V_VAR1)

    
    def table_connected(self, *args):
        """
        Table Section connected
        """
        self.smart_grid_table.table_connected(*args)
        self.need_time_sync_msg()
        self.reset_flow_config_timer()
        
    def module_placed(self, *args):
        """
        Module placed on Table Section
        """
        need_flow_update = self.smart_grid_table.module_placed(*args)

        if need_flow_update:
            self.reset_flow_config_timer()
        
    def table_neighbor_changed(self, *args):
        """
        Table Section neighbor changed
        """
        need_flow_update = self.smart_grid_table.table_neighbor_changed(*args)
        if need_flow_update:
            self.reset_flow_config_timer()
        
    def module_config_changed(self, *args):
        """
        Module config changed
        """
        need_flow_update = self.smart_grid_table.module_config_changed(*args)
        if need_flow_update:
            self.reset_flow_config_timer()
        
    def flow_disabled(self, *args):
        """
        FlowSegment on Table Section disabled
        """
        need_flow_update = self.smart_grid_table.flow_disabled(*args)
        if need_flow_update:
            self.reset_flow_config_timer()
        
    def buzzer_enabled(self, *args):
        """
        Module config changed
        """
        self.buzzer.set_enabled(*args)


    def power_boundaries_changed(self, *args):
        """
        Boundaries for load changed
        """
        voltage, load, value = args
        # TODO: Data validation?
        VOLTAGE_POWER_LOAD_BOUNDARIES[voltage][load] = value

    def reset_flow_config_timer(self):
        """
        Reset the flow config timer
        """
        self.send_flow_config_timer.cancel()
        self.send_flow_config_timer = start_daemon_timer(CONFIG_SEND_DELAY, self.need_flow_config_msg)

    def need_time_sync_msg(self):
        """
        Add message for time sync
        """
        self.add_message(SmartMessage(MessageTypes.TIME_SYNC))

    def need_flow_config_msg(self):
        """
        Add message for flow config
        """
        self.add_message(SmartMessage(MessageTypes.FLOW_CONFIG))

    def update_gui(self):
        # update gui with latest changes
        if self.gui is not None:
            self.gui.refresh()

    def need_reset_table_sections(self):
        """
        Add message for flow config
        """
        self.add_message(SmartMessage(MessageTypes.RESET_TABLES))




if __name__ == '__main__':
    serial_port = '/dev/ttyMySensorsGateway'
    baudrate = 115200
    if len(sys.argv) is 3:
        serial_port = sys.argv[1]
        baudrate = sys.argv[2]

    SmartGridApp(serial_port, baudrate)