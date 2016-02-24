#!/usr/bin/python

import struct
import logging
from analogpacket import AnalogPacket

class MaestroPacket(AnalogPacket):
    _HEADER = struct.pack('BB', 0xaa, 0x0c)

#################################
#### Maestro Channel Packets ####
#################################
# Maestro protocol packets that act on a specific motor channel.

class MaestroChannelPacket(MaestroPacket):
    """General packet structure for the Pololu Maestro for commands which act
    on a specific channel, using the Pololu protocol."""

    def __init__(self, channel, **kwargs):
        super(MaestroChannelPacket, self).__init__(channel=channel, **kwargs)

    def _prepare_field(self):
        raise NotImplementedError(
            "_prepare_field must be implemented in inheriting classes.")

class MaestroChannelSetPacket(MaestroChannelPacket):
    """Packets which are used to set different attributes, and don't expect
    a response."""
    # Command format is given as 4 bytes in Python struct format:
    # - 1st byte is for the command indicator
    # - 2nd byte is for the channel indicator
    # - 3rd byte is for the command value LSB
    # - 4th byte is for the command value MSB
    _COMMAND_FORMAT = '4B'

    def __init__(self, channel, **kwargs):
        super(MaestroChannelSetPacket, self).__init__(channel=channel, **kwargs)

    def _compile(self):
        return struct.pack(
            self._COMMAND_FORMAT,
            self._COMMAND_BYTE,
            self.channel,
            self._prepare_field() & 0x7f,
            (self._prepare_field() >> 7) & 0x7f)

    def _prepare_field(self):
        """A default implementation, inheriting classes with special cases
        should re-implement this method."""
        return getattr(self, self._COMMAND_FIELD)

    def __repr__(self):
        return "{0}(channel={1}, {2}={3})".format(
            self._CLASS_NAME, self.channel,
            self._COMMAND_FIELD, getattr(self, self._COMMAND_FIELD))

class MaestroChannelGetPacket(MaestroChannelPacket):
    """Packets which are used to get different attributes, hence expect a
    response."""
    # Command format is given as 2 bytes in a Python struct format:
    # - 1st byte is for the command indicator
    # - 2nd byte is for the channel indicator
    _COMMAND_FORMAT = '2B'
    # Reply format is given as 2 bytes in a Python struct format:
    # - 1st byte is for the reply value LSB
    # - 2nd byte is for the reply value MSB
    _REPLY_FORMAT = '2B'

    def __init__(self, channel):
        super(MaestroChannelGetPacket, self).__init__(channel=channel)

    def _compile(self):
        return struct.pack(
            self._COMMAND_FORMAT, self._COMMAND_BYTE, self.channel)

    def _get_answer(self, channel):
        raise NotImplementedError(
            "_get_answer should be implemented in inhereting classes.")

    def __repr__(self):
        return "{0}(channel={1})".format(
            self._CLASS_NAME, self.channel)

class MaestroSetTarget(MaestroChannelSetPacket):
    _CLASS_NAME = 'MaestroSetTarget'
    _COMMAND_BYTE = 0x04
    _COMMAND_FIELD = 'target'
    __QUARTER_US_MULTIPLIER = 4

    def __init__(self, channel, target):
        super(MaestroSetTarget, self).__init__(channel=channel, target=target)

    def _prepare_field(self):
        field = getattr(self, self._COMMAND_FIELD)
        return field * self.__QUARTER_US_MULTIPLIER

class MaestroSetSpeed(MaestroChannelSetPacket):
    _CLASS_NAME = 'MaestroSetSpeed'
    _COMMAND_BYTE = 0x07
    _COMMAND_FIELD = 'speed'

    def __init__(self, channel, speed):
        super(MaestroSetSpeed, self).__init__(channel=channel,
                                              speed=speed)

class MaestroSetAcceleration(MaestroChannelSetPacket):
    _CLASS_NAME = 'MaestroSetAcceleration'
    _COMMAND_BYTE = 0x09
    _COMMAND_FIELD = 'acceleration'

    def __init__(self, channel, acceleration):
        super(MaestroSetAcceleration, self).__init__(channel=channel,
                                                     acceleration=acceleration)

class MaestroGetPosition(MaestroChannelGetPacket):
    _CLASS_NAME = 'MaestroGetPosition'
    _COMMAND_BYTE = 0x10

    def __init__(self, channel):
        super(MaestroGetPosition, self).__init__(channel=channel)

    def _get_answer(self, channel):
        # We expect a 2-byte respone:
        lsb, = struct.unpack('B', channel.receive())
        msb, = struct.unpack('B', channel.receive())
        position = ((msb << 8) + lsb) / 4
        logging.debug("Got position {0} from channel {1}".format(
            position, self.channel))
        return position

################################
#### Maestro Script Packets ####
################################
# Maestro protocol packets that work with Maestro scripts.

class MaestroScriptPacket(MaestroPacket):
    def __init__(self, **kwargs):
        super(MaestroScriptPacket, self).__init__(**kwargs)

class MaestroRunScriptSubroutine(MaestroScriptPacket):
    _CLASS_NAME = 'MaestroRunScriptSubroutine'
    _COMMAND_FORMAT = '2B'
    _COMMAND_BYTE = 0x27
    _COMMAND_FIELD = 'sub_number'

    def __init__(self, sub_number):
        super(MaestroRunScriptSubroutine, self).__init__(sub_number=sub_number)

    def _compile(self):
        return struct.pack(
            self._COMMAND_FORMAT,
            self._COMMAND_BYTE,
            getattr(self, self._COMMAND_FIELD))

    def __repr__(self):
        return "{0}({1}={2})".format(
            self._CLASS_NAME,
            self._COMMAND_FIELD,
            getattr(self, self._COMMAND_FIELD))

class MaestroRunScriptSubroutineWithParam(MaestroRunScriptSubroutine):
    _CLASS_NAME = 'MaestroRunScriptSubroutineWithParam'
    _COMMAND_FORMAT = '4B'
    _COMMAND_BYTE = 0x28

    def __init__(self, sub_number, param):
        self.param = param
        super(MaestroRunScriptSubroutineWithParam, self).__init__(
            sub_number=sub_number)

    def _compile(self):
        return struct.pack(
            self._COMMAND_FORMAT,
            self._COMMAND_BYTE,
            self.sub_number,
            self.param & 0x7f,
            (self.param >> 7) & 0x7f)

    def __repr__(self):
        return "{0}({1}={2}, {3}={4})".format(
            self._CLASS_NAME,
            'sub_number', self.sub_number,
            'param', self.param)


class MaestroStopScriptSubroutine(MaestroScriptPacket):
    _CLASS_NAME = 'MaestroStopScriptSubroutine'
    _COMMAND_FORMAT = 'B'
    _COMMAND_BYTE = 0x24

    def __init__(self):
        super(MaestroStopScriptSubroutine, self).__init__()

    def _compile(self):
        return struct.pack(
            self._COMMAND_FORMAT,
            self._COMMAND_BYTE)

    def __repr__(self):
        return "{0}()".format(self._CLASS_NAME)
