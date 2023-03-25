from django.conf import settings
from dynamic_models.factory import ModelFactory
from dynamic_models.models import ModelSchema

SUPPORTED_DATA_TYPES = {"character": "django.db.models.CharField",
                        "integer": "django.db.models.IntegerField",
                        "boolean": "django.db.models.BooleanField",
                        }


def get_data_type(v: str) -> str:
    try:
        result = SUPPORTED_DATA_TYPES[v.lower()]
        kwargs = {'null': True, 'blank': True}
        if v == "character":
            kwargs['max_length'] = settings.DYNAMIC_MODELS['DEFAULT_CHAR_LENGHT']
            kwargs['default'] = ''

        return result, kwargs
    except KeyError:
        raise ValueError(f'Unrecognised type {v.lower()}')


def get_table_name(id: int) -> str:
    return '{}{}'.format(settings.DYNAMIC_MODELS['DYNAMIC_TABLE_PREFIX'], id)


def unregister_models():
    models = ModelSchema.objects.all()

    for model in models:
        ModelFactory(model).unregister_model()
