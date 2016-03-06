#!/usr/bin/python

import logging

from ast import literal_eval
from collections import namedtuple

from servo import maestropacket

def check_value_range(value, value_range):
    if value not in value_range:
        raise ValueError("Value {0} must be in range {1}".format(
            value, value_range))
    return value

_MaestroConnectionConfig = namedtuple(
    "MaestroConnectionConfig",
    ("connection_type", "baud_rate", "pan_channel", "tilt_channel",
     "pan_step_degree", "tilt_step_degree", "servo_min", "servo_max"))

class MaestroConnectionConfig(_MaestroConnectionConfig):
    _CONNECTION_TYPES = ('USB', 'UART')
    _CHANNELS = range(0, 6)

    def __init__(self, connection_type, baud_rate,
                 pan_channel, tilt_channel,
                 pan_step_degree, tilt_step_degree,
                 servo_min, servo_max):
        super(MaestroConnectionConfig, self).__init__(
            check_value_range(connection_type, self._CONNECTION_TYPES),
            baud_rate,
            check_value_range(pan_channel, self._CHANNELS),
            check_value_range(tilt_channel, self._CHANNELS),
            pan_step_degree,
            tilt_step_degree,
            servo_min,
            servo_max)
            #check_value_range(pan_step_degree, self._DEGREES),
            #check_value_range(tilt_step_degree, self._DEGREES)

    @classmethod
    def from_file(cls, filename):
        with file(filename, 'rt') as f:
            file_dict = literal_eval(f.read())
            return cls(
                file_dict['connection_type'],
                file_dict['baud_rate'],
                file_dict['pan_channel'],
                file_dict['tilt_channel'],
                file_dict['pan_step_degree'],
                file_dict['pan_step_degree'],
                file_dict['servo_min'],
                file_dict['servo_max'],
            )

    def to_file(self, filename):
        with file(filename, 'wt') as f:
            file_dict = {
                'connection_type': self.connection_type,
                'baud_rate': self.baud_rate,
                'pan_channel': self.pan_channel,
                'tilt_channel': self.tilt_channel,
                'pan_step_degree': self.pan_step_degree,
                'tilt_step_degree': self.tilt_step_degree,
                'servo_min': self.servo_min,
                'servo_max': self.servo_max,
            }

            f.write(str(file_dict))
