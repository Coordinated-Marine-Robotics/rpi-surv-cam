from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

# The event class, for example: events related to motion detection / internal
# system events, etc.
class EventClass(models.Model):
    class Meta:
        verbose_name_plural = "Event classes"
        managed = True

    def __unicode__(self):
        return 'Event class: ' + self.name

    name = models.CharField(max_length=100)
    visible = models.BooleanField(default=True)

# The event itself:
class Event(models.Model):
    class Meta:
        managed = True

    EVENT_SUCCESS = (0, 'Success')
    EVENT_FAILURE = (1, 'Failure')
    EVENT_SYSTEM_ERROR = (2, 'System Error')
    EVENT_INFO = (3, 'Info')
    EVENT_WARNING = (4, 'Warning')
    EVENT_STATUSES_CHOICES = (
        EVENT_SUCCESS,
        EVENT_FAILURE,
        EVENT_SYSTEM_ERROR,
        EVENT_INFO,
        EVENT_WARNING)

    description = models.TextField()
    event_class = models.ForeignKey(
        EventClass,
        on_delete=models.CASCADE,
        related_name="events")
    status = models.PositiveSmallIntegerField(
        choices=EVENT_STATUSES_CHOICES, default=EVENT_SUCCESS)
    time = models.DateTimeField(
        auto_now=False,
        auto_now_add=True)
    url = models.URLField(max_length = 200, blank=True)
    url_text = models.CharField(max_length = 50, blank=True)

    class register(object):
        def __init__(self, description, event_class, status,
                     url='', url_text=''):
            self._description = description
            self._event_class = EventClass.objects.get(name=event_class)
            self._status = status
            self._url = url
            self._url_text = url_text

        def __call__(self, func):
            def f(*args, **kwargs):
                Event.objects.create(
                    description=self._description,
                    event_class=self._event_class,
                    status=self._status[0],
                    url=self._url,
                    url_text=self._url_text)
                return func(*args, **kwargs)
            # This is instead of @wraps:
            f.func_name = func.func_name
            f.__doc__ = func.__doc__
            return f

__EVENTCLASS_SYSTEM_NAME = 'System'
__EVENTCLASS_MOTION_NAME = 'Motion'

def dropbox_motion_video_event(dropbox_url):
    motion_eventclass, _ = EventClass.objects.get_or_create(
        name=__EVENTCLASS_MOTION_NAME, visible = True)
    Event.objects.create(
        description="New motion video taken",
        event_class=motion_eventclass,
        status=Event.EVENT_INFO[0],
        url=dropbox_url,
        url_text="View video")

def dropbox_space_limit_event(mbs_remaining):
    system_eventclass, _ = EventClass.objects.get_or_create(
        name=__EVENTCLASS_SYSTEM_NAME, visible = True)
    Event.objects.create(
        description="Dropbox reaching space limit: {0} MBs remaining".format(mbs_remaining),
        event_class=system_eventclass,
        status=Event.EVENT_WARNING[0])

def get_recent_events():
    return Event.objects.order_by('-id')[:5]

def get_all_events():
    return Event.objects.order_by('-id')

def get_system_events():
    system_eventclass, _ = EventClass.objects.get_or_create(
        name=__EVENTCLASS_SYSTEM_NAME, visible = True)
    return Event.objects.filter(event_class = system_eventclass).order_by('-id')

def get_motion_events():
    motion_eventclass, _ = EventClass.objects.get_or_create(
        name=__EVENTCLASS_MOTION_NAME, visible = True)
    return Event.objects.filter(event_class = motion_eventclass).order_by('-id')

