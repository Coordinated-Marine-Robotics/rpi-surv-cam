from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Camera(models.Model):
    RESOLUTION_CHOICES = (
        ("640x480", "640x480"),
        ("1296x730", "1296x730"),
        ("1296x972", "1296x972"),
        ("1024x768", "1024x768"),
        ("2592x1944", "2592x1944"),
        ("1920x1080", "1920x1080")
    )

    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    stream_url = models.URLField()
    commands_queue = models.CharField(max_length=100)
    resolution = models.CharField(choices=RESOLUTION_CHOICES,
                                  max_length=100, default='1024x768')
    fps = models.IntegerField(default=30)
