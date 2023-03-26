from django.contrib import admin
from .models import IncrementableSingletonModel

# Register your models here.
admin.site.register(IncrementableSingletonModel)
