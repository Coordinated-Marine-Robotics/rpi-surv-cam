#!/usr/bin/python

import os
import serial
import logging

import maestropacket

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

class MaestroConnection(object):
    def __init__(self):
        logging.info("New MaestroConnection created")
        self._connection = None

    def __del__(self):
        if not self._connection.closed:
            self.close()

    # TODO: add enter and exit

    def close(self):
        logging.info("MaestroConnection closed")
        self._connection.close()

    def send(self, command):
        if not isinstance(command, maestropacket.MaestroPacket):
            raise TypeError(
                "'command' attribute must be of type "
                "'MaestroPacket' but is of type {0}".format(
                    type(command)))

        logging.info("Sending command {0}".format(repr(command)))

        # All commands write something to the Maestro:
        self._connection.write(str(command))

        # Some commands need to get back values from the Maestro:
        if isinstance(command, maestropacket.MaestroChannelGetPacket):
            # We let the command use the channel to get back the answer:
            return command._get_answer(self)

        # Default return value:
        return 0

    def receive(self):
        return self._connection.read()

class MaestroUSBConnection(MaestroConnection):
    def __init__(self):
        super(MaestroUSBConnection, self).__init__()
        # When configured for Dual USB, the Maestro is available
        # on /dev/ttyACM0:
        self._connection = serial.Serial('/dev/ttyACM0')

class MaestroUARTConnection(MaestroConnection):
    # The baud rate can be changed using the Polulo Maestro Control center.
    # This value is the current default value used for our configuration:
    __BAUD_RATE = 9600

    def __init__(self):
        super(MaestroUARTConnection, self).__init__()
        # When configured for serial, the Maestro is available on /dev/ttyAMA0:
        self._connection = serial.Serial(
            '/dev/ttyAMA0', baudrate = self.__BAUD_RATE)

class MaestroMockConnection(MaestroConnection):
    # A mock connection used for testing the servo commands

    class MockStream(object):
        def __init__(self):
            self.closed = False

        def write(self, stream):
            pass

        def read(self):
            return os.urandom(1)

        def close(self):
            self.closed = True

    def __init__(self):
        super(MaestroMockConnection, self).__init__()
        self._connection = self.MockStream()
