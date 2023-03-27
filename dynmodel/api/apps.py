from django.apps import AppConfig
from django.contrib import admin


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'dynamic model api'

    def _register_models(self):
        from dynamic_models.models import ModelSchema

        models = ModelSchema.objects.all()

        for model in models:
            admin.site.register(model.as_model())

    def ready(self):
        self._register_models()
