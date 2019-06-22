import serial
import time

from logger import log
from smart_grid_messaging import *


# Mysensors protocol types
# ref https://www.mysensors.org/download/serial_api_20
class MySenTypes:
    S_CUSTOM = 23
    V_VAR1 = 24
    V_VAR2 = 25
    V_VAR3 = 26
    V_VAR4 = 27
    V_VAR5 = 28
    V_RGB = 40

    @staticmethod
    def types():
        return vars(MySenTypes).values()

    @staticmethod
    def MySenType_to_SmartGridType(mysen):
        d = { 
            MySenTypes.S_CUSTOM: MessageTypes.TABLE_CONNECTED,
            MySenTypes.V_VAR2: MessageTypes.MODULE_PLACED,
            MySenTypes.V_VAR3: MessageTypes.NEIGHBOR_CHANGED
        }
        return d.get(mysen, -1)


class MySenCommands:
    PRESENT, SET, REQ, INTERNAL, STREAM = range(5)

    @staticmethod
    def types():
        return vars(MySenCommands).values()


class MySenMessage(object):
    def __init__(self,node_id,child_id,command,ack,type,payload):
        self.node_id = node_id
        self.child_id = child_id
        self.command = command
        self.ack = ack
        self.type = type
        self.payload = int(payload) if payload.isdigit() else payload

    def __repr__(self):
        return 'command {0}, type {1}, payload {2}'.format(self.command, self.type, self.payload)

class GatewayConnector(object):
    def __init__(self, message_func, serial_port, baudrate):
        self.message_func = message_func
        self.serial_port = serial_port
        self.baudrate = baudrate
        self.ser = serial.Serial()

    def send_serial_message(self, table_section_id, payload, command, type, child_id=0):
        message = '{0};{1};{2};0;{3};{4}\n'.format(table_section_id, child_id, command, type, payload)
        # log(message)
        if self.ser.isOpen():
            self.ser.write(message)
        else:
            log('Unable to send serial message, serial connection closed.')

    def handle_incoming_message(self, data_line):
        message = self.validate_data(data_line)
        if not message:
            log('Incorrect data format:', serial_data.strip())
            return
        if message.node_id is 0:
            log('from gateway: ', message)
        elif message.command in MySenCommands.types() and message.type in MySenTypes.types():
            s_message = SmartMessage(
                MySenTypes.MySenType_to_SmartGridType(message.type),
                (message.node_id, message.child_id, message.payload)
            )
            self.message_func(s_message)


    def validate_data(self, data_line):
        data_array = data_line.split(';')

        # Check if data contains 6 elements and ends with \n
        if len(data_array) is not 6 or data_line[-1] != '\n':
            return None

        # Check if each data is a digit except last (which is the payload)
        for data in data_array[:5]:
            if not data.isdigit():
                return None

        # Return message object 
        return MySenMessage(
            int(data_array[0]),
            int(data_array[1]),
            int(data_array[2]),
            int(data_array[3]),
            int(data_array[4]),
            data_array[5].rstrip() # strip newline
        )

    def start_serial_read(self):
        while 1:
            while not self.ser.isOpen():
                try:
                    self.ser = serial.Serial(self.serial_port, self.baudrate, timeout=1)
                    log('Serial connected')
                except:
                    log('No connection found on {0}...'.format(self.serial_port))
                    time.sleep(5) # If no serial connection found, sleep 5 sec
            try:
                serial_data = self.ser.readline()
                if serial_data.strip() != '':
                    self.handle_incoming_message(serial_data)
                else:
                    time.sleep(0.1)
            except serial.SerialException:
                self.ser.close()
                log('Disconnected serial')
            except KeyboardInterrupt:
                self.ser.close()
                break


if __name__ == "__main__":
    serial_port = '/dev/ttyMySensorsGateway'
    baudrate = 115200

    import sys
    if len(sys.argv) is 3:
        serial_port = sys.argv[1]
        baudrate = sys.argv[2]

    def msg_func(msg):
        log(msg)
        
    gw_conn = GatewayConnector(msg_func, serial_port, baudrate)
    gw_conn.start_serial_read()
