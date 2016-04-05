#!/usr/bin/python

from datetime import timedelta

## Broker settings:
BROKER_URL = 'amqp://guest:guest@localhost:5672//'

# List of modules to import when celery starts:
CELERY_IMPORTS = ('proj.tasks', )

## Using memcached to store task states and results (only for dev...)
#CELERY_RESULT_BACKEND = 'cache+memchaced://127.0.0.1:11211/'

CELERYBEAT_SCHEDULE = {
    'check-motion-dir': {
        'task': 'proj.tasks.upload_motion_to_dropbox', 
        'schedule': timedelta(seconds = 30),
        'args': ("/home/pi/motion_data", "/home/pi/dropbox"),
    }
}
