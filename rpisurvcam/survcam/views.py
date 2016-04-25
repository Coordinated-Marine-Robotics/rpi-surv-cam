import socket
import urllib2
import threading
from os import path
from time import sleep

import pika

from django.shortcuts import render
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required

from survcam.models import Camera
from events.models import Event, EventClass, get_recent_events

from .servotargetmanager import ServoTargetManager

#TODO: remove hardcoded dependency in motion's port numbers?
@login_required
def get_motion_stream_url(request):
    return request.build_absolute_uri('/')[:-1] + ':8081/'

@login_required
def get_motion_snapshot_url(request):
    return request.build_absolute_uri('/')[:-1] + ':8082/0/action/snapshot'

@login_required
def index(request):
    return render(
	    request,
            'survcam/stream.html',
            {'camera': Camera.objects.first(),
             'stream_url': get_motion_stream_url(request),
             'events': get_recent_events()})

@login_required
def update_target(request):
    return JsonResponse(
        {'pan_target': ServoTargetManager().get_target('pan'),
        'tilt_target': ServoTargetManager().get_target('tilt')})

@login_required
def move(request):
    target = request.POST['target']
    axis = request.POST['axis']

    queue_name = Camera.objects.first().commands_queue
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue = queue_name)
    channel.basic_publish(exchange='',
                          routing_key=queue_name,
                          body=(target + '@' + axis))
    connection.close()

    ServoTargetManager().set_target(axis, target)
    return JsonResponse({'target': ServoTargetManager().get_target(axis)})

@login_required
def snapshot(request):
    # Ask motion to take a snapshot
    urllib2.urlopen(get_motion_snapshot_url(request)).read()
    # Give the file time to be written
    sleep(1)
    # Read file contents and return in response
    #TODO: remove hardcoded dependency in motion's data directory
    snapshot_file = open('/home/pi/motion_data/lastsnap.jpg','rb')
    response = HttpResponse(snapshot_file.read())
    response['Content-Type'] = 'mimetype/submimetype'
    response['Content-Disposition'] = (
        'attachment; filename=%s' %
        path.basename(path.realpath(snapshot_file.name)))
    return response
