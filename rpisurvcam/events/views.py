from django.shortcuts import render
from .models import Event, EventClass
from .models import get_all_events, get_system_events, get_motion_events, get_dropbox_events

def events(request):
    return render(
            request,
            'events/events.html',
            {'all_events': get_all_events(),
             'system_events': get_system_events(),
             'motion_events': get_motion_events(),
             'dropbox_events': get_dropbox_events()})
