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
        def __init__(self, description, event_class_name, status,
                     url='', url_text=''):
            self._description = description
            self._event_class_name = event_class_name
            self._status = status
            self._url = url
            self._url_text = url_text

        def __call__(self, func):
            def f(*args, **kwargs):
                # We query the event class here so the view won't have any
                # side effects on import. This can also be handled using
                # OperationalError exception in the __init__ part:
                event_class, _ = EventClass.objects.get_or_create(name=self._event_class_name)
                Event.objects.create(
                    description=self._description,
                    event_class=event_class,
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
__EVENTCLASS_DROPBOX_NAME = 'Dropbox'

def new_motion_detected_event(filename):
    motion_eventclass, _ = EventClass.objects.get_or_create(
        name=__EVENTCLASS_MOTION_NAME, visible = True)
    event = Event.objects.create(
        description="Motion detected! A video was taken",
        event_class=motion_eventclass,
        status=Event.EVENT_WARNING[0],
        url='/download-motion?filename=' + filename,
        url_text="Download video")
    return event.id

def dropbox_motion_video_event(dropbox_url):
    dropbox_eventclass, _ = EventClass.objects.get_or_create(
        name=__EVENTCLASS_DROPBOX_NAME, visible = True)
    Event.objects.create(
        description="Motion video was uploaded to Dropbox",
        event_class=dropbox_eventclass,
        status=Event.EVENT_SUCCESS[0],
        url=dropbox_url,
        url_text="View video")

def dropbox_space_limit_event(mbs_remaining):
    dropbox_eventclass, _ = EventClass.objects.get_or_create(
        name=__EVENTCLASS_DROPBOX_NAME, visible = True)
    Event.objects.create(
        description="Dropbox reaching space limit: {0} MBs remaining".format(mbs_remaining),
        event_class=dropbox_eventclass,
        status=Event.EVENT_WARNING[0])

def dropbox_upload_error_event():
    dropbox_eventclass, _ = EventClass.objects.get_or_create(
        name=__EVENTCLASS_DROPBOX_NAME, visible = True)
    Event.objects.create(
        description="Error occurred while trying to upload video to Dropbox",
        event_class=dropbox_eventclass,
        status=Event.EVENT_FAILURE[0],
        url=settings.DROPBOX_VIDEOS_URL,
        url_text="is it full?")

def remove_motion_video_url(event_id):
    event = Event.objects.get(id=event_id)
    event.url = ''
    event.url_text = ''
    event.save()

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

def get_dropbox_events():
    dropbox_eventclass, _ = EventClass.objects.get_or_create(
        name=__EVENTCLASS_DROPBOX_NAME, visible = True)
    return Event.objects.filter(event_class = dropbox_eventclass).order_by('-id')
