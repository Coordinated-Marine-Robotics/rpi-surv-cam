from django.shortcuts import render, render_to_response
from django.http import HttpResponse

from survcam.models import Camera
import pika
import socket

def index(request):
	return render_to_response('survcam/stream.html',{'camera' : Camera.objects.first(), 'stream_url' : request.build_absolute_uri('/')[:-1] + ':8081/' })

def move(request):
	target = request.GET['target']
	axis = request.GET['axis']

	queue_name = Camera.objects.first().commands_queue
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()
	channel.queue_declare(queue = queue_name)
	channel.basic_publish(exchange='', routing_key=queue_name, body=(target + '@' + axis))
	connection.close()
	return HttpResponse('OK')
