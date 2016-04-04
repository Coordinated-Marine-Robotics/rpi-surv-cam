from django.shortcuts import render, render_to_response
from django.http import HttpResponse
from survcam.models import Camera
from events.models import Event, EventClass
import pika
import socket
import urllib2
from os import path
from time import sleep

#TODO: remove hardcoded dependency in motion's port numbers?
def get_motion_stream_url(request):
    return request.build_absolute_uri('/')[:-1] + ':8081/'

def get_motion_snapshot_url(request):
    return request.build_absolute_uri('/')[:-1] + ':8082/0/action/snapshot'

def get_recent_events():
    return Event.objects.order_by('-id')[:2]

def get_all_events():
    return Event.objects.order_by('-id')

def index(request):
    return render_to_response(
            'survcam/stream.html',
            {'camera': Camera.objects.first(),
             'stream_url': get_motion_stream_url(request),
             'events': get_recent_events()})

#@Event.register('admin', "get_all_events called",
#                "System", Event.EVENT_INFO)
def events(request):
    return render_to_response(
            'survcam/events.html',
            {'events': get_all_events()})

def move(request):
    # TODO: do connection to queue only once!
    target = request.GET['target']
    axis = request.GET['axis']

    queue_name = Camera.objects.first().commands_queue
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue = queue_name)
    channel.basic_publish(exchange='',
                          routing_key=queue_name,
                          body=(target + '@' + axis))
    connection.close()
    return HttpResponse('OK')

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
