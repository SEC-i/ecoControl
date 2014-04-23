from django.db import models

class Settings(models.Model):
    key = models.CharField(max_length = 100)
    value = models.CharField(max_length = 255)
