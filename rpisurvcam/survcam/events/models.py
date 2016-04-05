from __future__ import unicode_literals

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User

# The event class, for example: events related to motion detection / internal
# system events, etc.
class EventClass(models.Model):
    class Meta:
        verbose_name_plural = "Event classes"

    def __unicode__(self):
        return 'Event class: ' + self.name

    name = models.CharField(max_length=100)
    visible = models.BooleanField(default=True)

# The event itself:
class Event(models.Model):
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
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="events")
    time = models.DateTimeField(
        auto_now=False,
        auto_now_add=True)

    class register(object):
        def __init__(self, user, description, event_class, status):
            self._user = User.objects.get(username=user)
            self._description = description
            self._event_class = EventClass.objects.get(name=event_class)
            self._status = status

        def __call__(self, func):
            def f(*args, **kwargs):
                Event.objects.create(
                    user=self._user,
                    description=self._description,
                    event_class=self._event_class,
                    status=self._status[0])
                return func(*args, **kwargs)
                # This is instead of @wraps:
            f.func_name = func.func_name
            f.__doc__ = func.__doc__
            return f
