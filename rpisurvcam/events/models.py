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
    EVENT_STATUSES_CHOICES = (
        EVENT_SUCCESS,
        EVENT_FAILURE,
        EVENT_SYSTEM_ERROR,
        EVENT_INFO)

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
    url = models.URLField(max_length = 200, null=True)
    url_text = models.CharField(max_length = 50, null=True)

    class register(object):
        def __init__(self, user, description, event_class, status,
                     url=None, url_text=None):
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

def get_recent_events():
    return Event.objects.order_by('-id')[:2]

def get_all_events():
    return Event.objects.order_by('-id')
