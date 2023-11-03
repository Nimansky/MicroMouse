import serial
import struct
from enum import IntEnum

class CommandType(IntEnum):
    SEND_SENSOR_DATA = 0
    TURN_LEFT = 1
    TURN_RIGHT = 2
    MOVE_FORWARD = 3
    MOVE_BACKWARD = 4

class Sensor(IntEnum):
    """
    This enum contains the sensors that can be queried on the MicroMouse, use these EnumTypes

    a) as keys access the map returned by gather_sensor_data()

    b) as param to read_sensor()
    """
    RPM_LEFT = 0
    RPM_RIGHT = 1
    COLLISION_FRONT_RIGHT = 2
    COLLISION_FRONT_LEFT = 3
    COLLISION_RIGHT = 4
    COLLISION_LEFT = 5
    DISTANCE_FRONT = 6

INIT_SEQUENCE = 0x1A40

RESPONSE_OKAY = 1
RESPONSE_FAULTY = 0


ser = serial.Serial('/dev/ttyAMA0', 115200)


def __sendCommand__(cmd, param):
    msg = (INIT_SEQUENCE + cmd).to_bytes(2, 'big') + param.to_bytes(4, 'big')
    ser.write(msg)
    return ser.read(6)

def turn_left(steps):
    """
    turns the MicroMouse left in 90-degree-steps

    Parameters: the amount of 90 degree steps

    Returns: RESPONSE_OKAY if transmission succeeded and movement completed
    """
    res = __sendCommand__(CommandType.TURN_LEFT, steps)
    resCode = RESPONSE_OKAY if (struct.unpack('>H', res[0:2])[0] >> 4) == 0x1A4 else RESPONSE_FAULTY #need big endian here
    return resCode

def turn_right(steps):
    """
    turns the MicroMouse right in 90-degree-steps

    Parameters: the amount of 90 degree steps

    Returns: RESPONSE_OKAY if transmission succeeded and movement completed
    """
    res = __sendCommand__(CommandType.TURN_RIGHT, steps)
    resCode = RESPONSE_OKAY if (struct.unpack('>H', res[0:2])[0] >> 4) == 0x1A4 else RESPONSE_FAULTY #need big endian here
    return resCode

def move_forward(steps):
    """
    moves the mouse forward in the maze

    Parameters: amount of maze fields to move

    Returns: RESPONSE_OKAY if transmission succeeded and movement completed
    """
    res = __sendCommand__(CommandType.MOVE_FORWARD, steps)
    resCode = RESPONSE_OKAY if (struct.unpack('>H', res[0:2])[0] >> 4) == 0x1A4 else RESPONSE_FAULTY #need big endian here
    return resCode

def move_backwards(steps):
    """
    moves the mouse backwards in the maze

    Parameters: amount of maze fields to move

    Returns: RESPONSE_OKAY if transmission succeeded and movement completed
    """
    res = __sendCommand__(CommandType.MOVE_BACKWARD, steps)
    resCode = RESPONSE_OKAY if (struct.unpack('>H', res[0:2])[0] >> 4) == 0x1A4 else RESPONSE_FAULTY #need big endian here
    return resCode


def read_sensor(sensor):

    """read_sensor(sensor)
    
    Parameters: the sensor to be queried (instance of IntEnum Sensor)

    Returns:
    tuple [code, data] - RESPONSE_OKAY/RESPONSE_FAULTY and the data (the latter can be garbage if RESPONSE_FAULTY)
    """

    if isinstance(sensor, Sensor):
        res = __sendCommand__(CommandType.SEND_SENSOR_DATA, sensor)
        resCode = RESPONSE_OKAY if (struct.unpack('>H', res[0:2])[0] >> 4) == 0x1A4 else RESPONSE_FAULTY #need big endian here
        data = res[2:6]
        if sensor == Sensor.RPM_LEFT or sensor == Sensor.RPM_RIGHT:
            data = struct.unpack('f', data)[0]
        elif sensor == Sensor.DISTANCE_FRONT:
            data = struct.unpack('I', data)[0]
        else: #collision sensors
            data = bool(data[0]) #invert bc collision sensors output 0 if True
        return [resCode, data]

def gather_sensor_data():
    """gather_sensor_data()

    Make sure to only call this method about once each 100ms, because any faster than that can cause UART Overrun on the MicroMouse (keep in mind each poll is 6 requests + 6 responses)
    For that reason, this method is better to use as a monitoring tool; if specific sensor data is necessary more often for control, poll read_sensor() on the specific sensor instead!

    Returns:
    dictionary {key, data} - key is instance of IntEnum Sensor, data is the data the sensor currently holds

    """
    dict = {}
    for s in Sensor:
        resCode, data = read_sensor(s)
        if(resCode == RESPONSE_OKAY):
            dict.update({s: data})
    return dict