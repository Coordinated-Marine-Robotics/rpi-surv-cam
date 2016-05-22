from celery import Celery
import sys

if __name__ == "__main__":
    app = Celery('celerytasks', broker='amqp://guest:guest@localhost:5672//')
    app.send_task('events.tasks.new_motion_detected',args=[str(sys.argv[1])])
