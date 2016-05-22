#!/usr/bin/python
from __future__ import absolute_import
from celery import app, Celery
from .models import dropbox_space_limit_event, dropbox_motion_video_event
from .models import new_motion_detected_event, remove_motion_video_url
from .models import dropbox_upload_error_event
from django.conf import settings
import os
import subprocess

app = Celery('celerytasks', broker='amqp://guest:guest@localhost:5672//')

DROPBOX_FREE_THRESH_MB = 100
CAPACITY_THRESH_MB = 10
MB_IN_BYTES = 1048576.0

dropbox_videos = "/videos"
dropbox_images = "/images"

def is_motion_dir_full(motion_path):
    os.chdir(motion_path)
    curr_size = sum(os.path.getsize(f) for f in os.listdir('.')
                    if os.path.isfile(f))
    curr_size_mb = curr_size / MB_IN_BYTES
    return (curr_size_mb > CAPACITY_THRESH_MB)

@app.task
def alert_if_dropbox_full():
    # get dropbox account info
    proc = subprocess.Popen([settings.DROPBOX_UPLOADER,'info'],
        stdout=subprocess.PIPE)
    output_lines = proc.stdout.read().split('\n')
    data = dict()
    for pair in (x.split(':\t') for x in output_lines if ':\t' in x):
        data[pair[0]] = pair[1]

    # check free space
    free_space = int(data['Free'].split()[0])
    if free_space < DROPBOX_FREE_THRESH_MB:
        # write warning event to web app
       dropbox_space_limit_event(free_space)
    return free_space

@app.task
def upload_motion_to_dropbox():
    motion_path = settings.MOTION_TARGET_DIR

    if not is_motion_dir_full(motion_path):
        pass

    video_files = os.path.join(motion_path, "*.avi")
    image_files = os.path.join(motion_path, "*.jpg")

    # upload videos to dropbox
    proc = subprocess.Popen([settings.DROPBOX_UPLOADER, 'upload'] +
                            filter(
                                lambda f:f.endswith('avi'),
                                os.listdir(motion_path)) +
                            [dropbox_videos],
                            stdout=subprocess.PIPE)
    # get new remote videos and add events to web app
    # assuming output line format:  > Uploading "local_path" to "remote_path"... DONE
    files = proc.stdout.read().split('\n')
    for item in (f.split('"') for f in files if 'DONE' in f):
        remote_file = item[3]
        proc = subprocess.Popen([settings.DROPBOX_UPLOADER, 'share',
                                remote_file], stdout=subprocess.PIPE)
        # assuming output format:  > Share link: https://db.tt/a9xJoX9X
        shared_url = proc.stdout.read().split()[3]
        # create event for new motion video
        dropbox_motion_video_event(shared_url)

    # delete videos from Rpi
    os.system("rm -f " + os.path.join(motion_path, "*.avi"))

    # upload images to dropbox and delete from Rpi
    #os.system(settings.DROPBOX_UPLOADER + " upload " + image_files + " " + dropbox_images)
    #os.system("rm -f " + os.path.join(motion_path, "*.jpg"))

    alert_if_dropbox_full()

@app.task
def new_motion_detected(filepath):
    if not os.path.isfile(filepath):
        return

    # Add event to let web app users know motion was detected
    event_id = new_motion_detected_event(os.path.basename(filepath))

    # Upload motion video to Dropbox
    proc = subprocess.Popen([settings.DROPBOX_UPLOADER, 'upload',
                            filepath, dropbox_videos],
                            stdout=subprocess.PIPE)

    # Get remote video URL and add event to web app,
    # assuming output line format:  > Uploading "local_path" to "remote_path"... DONE
    output = proc.stdout.read()
    if 'DONE' not in output:
        # There was an error while uploading the video to Dropbox, abort.
        dropbox_upload_error_event()
        return
    remote_file = output.split('"')[3]
    proc = subprocess.Popen([settings.DROPBOX_UPLOADER, 'share', remote_file],
                            stdout=subprocess.PIPE)
    # assuming output format:  > Share link: https://db.tt/a9xJoX9X
    shared_url = proc.stdout.read().split()[3]

    # Create event for new motion video
    dropbox_motion_video_event(shared_url)

    # Remove option to download local video because it's about to be deleted
    remove_motion_video_url(event_id)

    # delete video from motion data directory
    os.remove(filepath)
