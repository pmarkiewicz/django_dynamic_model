from django.db import models


class IdGenerator(models.Model):
    last_id = models.IntegerField()
