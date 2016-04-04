from django.contrib import admin

# Register your models here.

from .models import Camera
from events.models import EventClass, Event

admin.site.register(Camera)
admin.site.register(EventClass)
admin.site.register(Event)
