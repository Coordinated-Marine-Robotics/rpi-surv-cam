from django.shortcuts import render_to_response
from .models import Event, EventClass, get_all_events

def events(request):
    return render_to_response(
            'events/events.html',
            {'events': get_all_events()})
