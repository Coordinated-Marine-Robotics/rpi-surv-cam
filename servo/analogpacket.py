#!/usr/bin/python

"""The idea here is to create a representation of the data being sent to another
connected device via some serial/parallel connection. The data is represented
abstractly as possible, and then translated to its 'on-the-wire' format as
the matching protocol dictates. So basically, this tries to set apart the
protocol implementation and its practical data representation as much as
possible."""

import struct

class AnalogPacket(object):
    _HEADER           = None
    _COMMAND_FORMAT   = None
    _FINAL_FORMAT     = None
    _COMPILED_COMMAND = None

    def __init__(self, **kwargs):
        # This implicitly sets all keyword arguments as attributes of this class
        # and inheriting classes objects:
        for name, value in kwargs.iteritems():
            setattr(self, name, value)

        self._COMPILED_COMMAND = self.compile()

    def compile(self):
        # Assuming header, if exists, is constant:
        if self._HEADER:
            return self._HEADER + self._compile()
        return self._compile()

    def _compile(self):
        raise NotImplementedError(
            "_compile must be implemented in inheriting classes.")

    @staticmethod
    def from_data(cls, data):
        pass

    def __str__(self):
        return self._COMPILED_COMMAND
