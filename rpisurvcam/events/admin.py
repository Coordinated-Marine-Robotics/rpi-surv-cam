from django.contrib import admin

from .models import EventClass, Event

admin.site.register(EventClass)
admin.site.register(Event)
