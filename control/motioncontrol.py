#!/usr/bin/python

import logging
from operator import lt, gt

logger = logging.getLogger("appLogger")

from maestroconfig import MaestroConnectionConfig
from servo import maestropacket

class CameraMotionControl(object):

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

        # The channel id's on the Maestro board for each axis:
        self._channels = {'pan': self._config.pan_channel,
                          'tilt': self._config.tilt_channel}

        # Movment range (in [us]) in each axis:
        self._range = {
            'pan': (self._config.pan_servo_min, self._config.pan_servo_max),
            'tilt': (self._config.tilt_servo_min, self._config.tilt_servo_max)}

        # Starting position of each axis:
        self._start_positions = {}

        # Current position of each axis:
        self._positions = {}

        # Translation of the start positions into degrees. Each axis can move
        # between -90 to 90 degrees:
        self._degrees = {}

        # How many steps in [us] does a motor in each axis should move in order
        # to advance in one degree:
        self._one_degree_steps = {}

        self.__setup_pan_tilt_params()

        if reset:
            self._reset_positions()

    def __setup_pan_tilt_params(self):
        self._start_positions['pan'] = (
            int((self._config.pan_servo_min +
                 self._config.pan_servo_max) / 2))
        self._start_positions['tilt'] = (
            int((self._config.tilt_servo_min +
                 self._config.tilt_servo_max) / 2))

        self._one_degree_steps['pan'] = (
            (self._config.pan_servo_max - self._start_positions['pan']) /
            self.__HALF_AXIS_DEGREES)
        self._one_degree_steps['tilt'] = (
            (self._config.tilt_servo_max - self._start_positions['tilt']) /
            self.__HALF_AXIS_DEGREES)

    def __to_degrees(self, steps, axis):
        return steps / self._one_degree_steps[axis]

    def __degree_to_target(self, degree, axis):
        return (self._start_positions[axis] +
                degree * self._one_degree_steps[axis])

    def __get_relative_position(self, position, axis):
        return position - self._start_positions[axis]

    def __to_degrees_relative(self, position, axis):
        return self.__to_degrees(
            self.__get_relative_position(position, axis), axis)

    def reset(self):
        self._reset_positions()

    def _reset_positions(self):
        logger.info("Resetting pan channel (#{0}) to {1}".format(
            self._config.pan_channel, self._start_positions['pan']))
        self._positions['pan'] = (self.__set_and_get_position(
            'pan', self._start_positions['pan']))
        self._degrees['pan'] = (self.__to_degrees_relative(
            self._positions['pan'], 'pan'))

        logger.info("Resetting tilt channel (#{0}) to {1}".format(
            self._config.tilt_channel, self._start_positions['tilt']))
        self._positions['tilt'] = (self.__set_and_get_position(
            'tilt', self._start_positions['tilt']))
        self._degrees['tilt'] = self.__to_degrees_relative(
            self._positions['tilt'], 'tilt')

        logger.debug("Reset pan and tilt to {:+.1f} and {:+.1f} "
                     "degrees".format(self._degrees['pan'],
                                      self._degrees['tilt']))

    def __set_and_get_position(self, axis, position):
        self._conn.send(
            maestropacket.MaestroSetTarget(self._channels[axis], position))

        # In order to prevent the delay when using accelaration, position is
        # not sampled accurately from the Maestro:
        servo_min, servo_max = self._range[axis]
        if position <= servo_min:
            return servo_min
        elif position >= servo_max:
            return servo_max

        return position

    def move(self, axis, step, limiter, op):
        if op(self._positions[axis], limiter):
            self._positions[axis] = self.__set_and_get_position(
                axis, self._positions[axis] + step)
            self._degrees[axis] = self.__to_degrees_relative(
                self._positions[axis], axis)

    def move_to_degree(self, axis, degree):
        self.__set_and_get_position(
            axis, self.__degree_to_target(degree, axis))

    def pan_left(self):
        self.move('pan', self._config.pan_step_degree,
                  self._config.pan_servo_max, lt)
        logger.debug("Panned left to {:+.1f} degrees".format(
            self._degrees['pan']))

    def pan_right(self):
        self.move('pan', -(self._config.pan_step_degree),
                  self._config.pan_servo_min, gt)
        logger.debug("Panned right to {:+.1f} degrees".format(
            self._degrees['pan']))

    def tilt_up(self):
        self.move('tilt', self._config.tilt_step_degree,
                  self._config.tilt_servo_max, lt)
        logger.debug("Tilted up to {:+.1f} degrees".format(
            self._degrees['tilt']))

    def tilt_down(self):
        self.move('tilt', -(self._config.tilt_step_degree),
                  self._config.tilt_servo_min, gt)
        logger.debug("Tilted down to {:+.1f} degrees".format(
            self._degrees['tilt']))
