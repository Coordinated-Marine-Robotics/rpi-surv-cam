from django.shortcuts import render, render_to_response
from django.http import HttpResponse

from survcam.models import Camera
import pika
import socket

def index(request):
	return render_to_response('survcam/stream.html',{'camera' : Camera.objects.first()})

def move(request):
	direction = request.GET['direction']

#	if(direction != 'left' and direction != 'right' and direction != 'up' and direction != 'down'):
#		return
	queue_name = Camera.objects.first().commands_queue
	connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
	channel = connection.channel()
	channel.queue_declare(queue = queue_name)
	channel.basic_publish(exchange='', routing_key=queue_name, body=('move_' + direction))
	connection.close()
	return HttpResponse('OK')
