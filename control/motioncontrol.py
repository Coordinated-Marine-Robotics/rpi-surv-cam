#!/usr/bin/python

import logging

logger = logging.getLogger("appLogger")

from maestroconfig import MaestroConnectionConfig
from servo import maestropacket

class CameraMotionControl(object):
    """This class controls the motion of the camera.
    TODO - finish documentation
    Each method either pan or tilts the camera by the required number of steps,
    where a step
    """

    __HALF_AXIS_DEGREES = 90

    def __init__(self, conn, config, reset=True):
        """@param conn: a MaestroConnection object, can be either a USB
        connection to the Maestro (MaestroUSBConnection) or a UART
        connection (MaestroUARTConnection).
        @param config: a MaestroConnectionConfig object, instantiated with
        relevant configuration parameters, either manually or from a file.
        @param reset: whether the pan-tilt servos should be reset to their
        initial positions (average of min. and max. positions)."""
        self._conn = conn
        self._config = config

        self._pan_position = None
        self._tilt_position = None

        self._start_position = int((self._config.servo_min +
                                    self._config.servo_max) / 2)

        # Get the amount of us for one degree:
        self.__one_degree_steps = (
            (self._config.servo_max - self._start_position) /
            self.__HALF_AXIS_DEGREES)

        # Translation of the start positions into degrees. Each axis can move
        # between -90 to 90 degrees:
        self._pan_degree = None
        self._tilt_degree = None

        # Destinations (targets) of each servo. We use this to identify whether
        # one of the axis is still in motion:
        self._destinations = {self._config.pan_channel: self._start_position,
                              self._config.tilt_channel: self._start_position}

        if reset:
            self._reset_positions()

    def __to_degrees(self, steps):
        return steps / self.__one_degree_steps

    def __get_relative_position(self, position):
        return position - self._start_position

    def __to_degrees_relative(self, position):
        return self.__to_degrees(self.__get_relative_position(position))

    def reset(self):
        self._reset_positions()

    def _reset_positions(self):
        logger.info("Resetting pan channel (#{0}) to {1}".format(
            self._config.pan_channel, self._start_position))
        self._pan_position = self.__set_and_get_position(
            self._config.pan_channel, self._start_position)
        self._pan_degree = self.__to_degrees_relative(self._pan_position)

        logger.info("Resetting tilt channel (#{0}) to {1}".format(
            self._config.tilt_channel, self._start_position))
        self._tilt_position = self.__set_and_get_position(
            self._config.tilt_channel, self._start_position)
        self._tilt_degree = self.__to_degrees_relative(self._tilt_position)

        logger.debug("Reset pan and tilt to {:+.1f} and {:+.1f} degrees".format(
            self._pan_degree, self._tilt_degree))


    def __set_and_get_position(self, channel, position):
        self._conn.send(maestropacket.MaestroSetTarget(channel, position))

        # In order to prevent the delay when using accelaration, position is
        # not sampled accurately from the Maestro:
        if position <= self._config.servo_min:
            return self._config.servo_min
        elif position >= self._config.servo_max:
            return self._config.servo_max

        return position

    def pan_left(self):
        if self._pan_position < self._config.servo_max:
            self._pan_position = self.__set_and_get_position(
                self._config.pan_channel,
                self._pan_position + self._config.pan_step_degree)
            self._pan_degree = self.__to_degrees_relative(self._pan_position)

            logger.debug("Panned left to {:+.1f} degrees".format(
                self._pan_degree))

    def pan_right(self):
        if self._pan_position > self._config.servo_min:
            self._pan_position = self.__set_and_get_position(
                self._config.pan_channel,
                self._pan_position - self._config.pan_step_degree)
            self._pan_degree = self.__to_degrees_relative(self._pan_position)

            logger.debug("Panned right to {:+.1f} degrees".format(
                self._pan_degree))

    def tilt_up(self):
        if self._tilt_position < self._config.servo_max:
            self._tilt_position = self.__set_and_get_position(
                self._config.tilt_channel,
                self._tilt_position + self._config.tilt_step_degree)
            self._tilt_degree = self.__to_degrees_relative(self._tilt_position)

            logger.debug("Tilted up to {:+.1f} degrees".format(
                self._tilt_degree))

    def tilt_down(self):
        if self._tilt_position > self._config.servo_min:
            self._tilt_position = self.__set_and_get_position(
                self._config.tilt_channel,
                self._tilt_position - self._config.tilt_step_degree)
            self._tilt_degree = self.__to_degrees_relative(self._tilt_position)

            logger.debug("Tilted down to {:+.1f} degrees".format(
                self._tilt_degree))
