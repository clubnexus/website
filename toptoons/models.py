from django.db import models

class TopToonsEntry(models.Model):
    month = models.IntegerField()
    data = models.CharField(max_length=20480)
    