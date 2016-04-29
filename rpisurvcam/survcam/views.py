import socket
import urllib2
import threading
from os import path
from time import sleep

import pika

from django.shortcuts import render
from django.views.generic import View
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpResponse, HttpResponseBadRequest
from django.http import JsonResponse, FileResponse
from django.template.response import TemplateResponse
from django.core import serializers
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required

from survcam.models import Camera
from events.models import Event, EventClass, get_recent_events

from .servotargetmanager import ServoTargetManager

#TODO: remove hardcoded dependency in motion's port numbers?
def get_motion_stream_url(request):
    return request.build_absolute_uri('/')[:-1] + ':8081/'

def get_motion_snapshot_url(request):
    return request.build_absolute_uri('/')[:-1] + ':8082/0/action/snapshot'

def is_stream_alive(request):
    try:
        return urllib2.urlopen(get_motion_stream_url(request),
                               timeout = 2).getcode() == 200
    except:
        return False

@login_required
def index(request):
    stream_active = is_stream_alive(request)
    return render(
        request,
            'survcam/stream.html',
            {'camera': Camera.objects.first(),
             'status': 'Live' if stream_active else 'Down',
             'stream_url': get_motion_stream_url(request) if stream_active
             else 'static/img/stream_down.png',
             'events': get_recent_events()})

@login_required
def update_status(request):
    events = TemplateResponse(request, 'events/events_contents.html',
                             {'events':get_recent_events()})
    events.render()

    stream_active = is_stream_alive(request)
    stream_status_html = TemplateResponse(request, 'survcam/camera_status.html',
                                     {'camera': Camera.objects.first(),
                                     'status': 'Live' if stream_active
                                      else False})
    return JsonResponse(
        {'stream_active': stream_active,
        'stream_status_html': stream_status_html.rendered_content,
        'events': events.rendered_content,
        'pan_target': ServoTargetManager().get_target('pan'),
        'tilt_target': ServoTargetManager().get_target('tilt')}, safe=False)

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
    try:
        urllib2.urlopen(get_motion_snapshot_url(request)).read()
    except:
        # motion is probably down, abort
        return HttpResponseBadRequest()
    # Give the file time to be written
    sleep(1)
    # Read file contents and return in response
    #TODO: remove hardcoded dependency in motion's data directory
    snapshot_file = open('/home/pi/motion_data/lastsnap.jpg','rb')
    response = FileResponse(snapshot_file);
    response['Content-Type'] = 'mimetype/submimetype'
    response['Content-Disposition'] = ('attachment; filename=%s' %
    path.basename(path.realpath(snapshot_file.name)))
    return response

@staff_member_required
@login_required
@Event.register("Camera turned ON", 'System', Event.EVENT_INFO)
def camera_on(request):
    return HttpResponse(200)

@staff_member_required
@login_required
@Event.register("Camera turned OFF", 'System', Event.EVENT_INFO)
def camera_off(request):
    return HttpResponse(200)
