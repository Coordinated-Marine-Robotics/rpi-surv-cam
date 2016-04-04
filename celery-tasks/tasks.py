#!/usr/bin/python

from celery import Celery
import os

app = Celery('tasks', broker='amqp://guest:guest@localhost:5672//')

CAPACITY_THRESH_MB = 10
MB_IN_BYTES = 1048576.0
UPLOAD_LOCK = '/home/pi/.upload_in_progress'
dropbox_videos = "/videos"
dropbox_images = "/images"

def is_motion_dir_full(motion_path):
        os.chdir(motion_path)
        curr_size = sum(os.path.getsize(f) for f in os.listdir('.') if os.path.isfile(f))
        curr_size_mb = curr_size / MB_IN_BYTES
        return (curr_size_mb > CAPACITY_THRESH_MB)

@app.task
def upload_motion_to_dropbox(motion_path, dropbox_path):
        if os.path.exists(UPLOAD_LOCK):  #TODO: remove this 'lock' and use Celery's
                return
        if not is_motion_dir_full(motion_path):
                return

        open(UPLOAD_LOCK,'w').close()

        video_files = os.path.join(motion_path, "*.avi")
        image_files = os.path.join(motion_path, "*.jpg")
        dropbox_uploader = os.path.join(dropbox_path, "dropbox_uploader.sh")

        os.system(dropbox_uploader + " upload " + video_files + " " + dropbox_videos)
        os.system("rm -f " + os.path.join(motion_path, "*.avi"))

        os.system(dropbox_uploader + " upload " + image_files + " " + dropbox_images)
        os.system("rm -f " + os.path.join(motion_path, "*.jpg"))

        os.remove(UPLOAD_LOCK)
