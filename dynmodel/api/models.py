from django.db import models


class IncrementableSingletonModel(models.Model):
    value = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.pk = 1
        super(IncrementableSingletonModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def next(self):
        self.value += 1
        self.save()

        return self.value
