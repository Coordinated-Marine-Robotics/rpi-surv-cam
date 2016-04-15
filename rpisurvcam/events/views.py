from django.shortcuts import render_to_response
from .models import Event, EventClass
from .models import get_all_events, get_system_events, get_motion_events

def events(request):
    return render_to_response(
            'events/events.html',
            {'all_events': get_all_events(),
             'system_events': get_system_events(),
             'motion_events': get_motion_events()})
