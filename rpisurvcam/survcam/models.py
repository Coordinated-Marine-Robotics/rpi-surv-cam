from __future__ import unicode_literals

from django.db import models
from django.core.exceptions import ValidationError

class Camera(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

    def clean(self):
        model = self.__class__
        if (model.objects.count() > 0 and self.id != model.objects.get().id):
            raise ValidationError("You can only create one Camera instance. \
            Please remove the first instance, \
            or change it's values instead of creating a new Camera.")
