import sys
import logging
import logging.handlers

import curses
import time

from servo import maestroconnection, maestropacket
from control.motioncontrol import CameraMotionControl
from control.maestroconfig import MaestroConnectionConfig

import pika

app_logger = logging.getLogger("appLogger")
servo_logger = logging.getLogger("servoLogger")
app_logger.setLevel(logging.DEBUG)
servo_logger.setLevel(logging.INFO)

syslog_handler = logging.handlers.SysLogHandler(address = '/dev/log')
syslog_handler.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
log_formatter = logging.Formatter(
    "%(asctime)s [%(name)s] <%(levelname)s> %(message)s",
    "%Y-%m-%d %H:%M:%S")

syslog_handler.setFormatter(log_formatter)
console_handler.setFormatter(log_formatter)

app_logger.addHandler(syslog_handler)
app_logger.addHandler(console_handler)

servo_logger.addHandler(syslog_handler)
servo_logger.addHandler(console_handler)

conn = maestroconnection.MaestroUSBConnection()
config = MaestroConnectionConfig.from_file('a.conf')
conn.send(maestropacket.MaestroSetAcceleration(config.pan_channel,acceleration=5))
conn.send(maestropacket.MaestroSetAcceleration(config.tilt_channel,acceleration=5))

cm_control = CameraMotionControl(conn, config, reset=True)

def callback(ch, method, properties, body):
        print(" [x] Received %r" % body)
	data = body.split('@')
	target = -1 * int(data[0])
	axis = data[1]
	cm_control.move_to_degree(axis, target)

def main():
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='camcmd')

        channel.basic_consume(callback,queue='camcmd',no_ack=True)
        channel.start_consuming()


if __name__ == '__main__':
    main()

