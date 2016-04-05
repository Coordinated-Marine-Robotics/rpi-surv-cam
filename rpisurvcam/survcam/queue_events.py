from django_socketio.events import on_message
from survcam.models import Camera
import pika

@on_message
def move_handler(request, socket, context, message):
    direction = message['direction']
    queue_name = Camera.objects.first().commands_queue
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost'))
    channel = connection.channel()
    channel.queue_declare(queue = queue_name)
    channel.basic_publish(
        exchange='', routing_key=queue_name, body=('move_' + direction))
    connection.close()

@on_finish
def finish_handler(request, socket, context, message):
    pass
