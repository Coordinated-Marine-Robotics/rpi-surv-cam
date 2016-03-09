from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Camera(models.Model):
	name = models.CharField(max_length=100)
	stream_url = models.URLField()
	commands_queue = models.CharField(max_length=100)

