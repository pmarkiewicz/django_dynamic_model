from django.conf import settings

SUPPORTED_DATA_TYPES = {"character": "django.db.models.CharField",
                        "integer": "django.db.models.IntegerField",
                        "boolean": "django.db.models.BooleanField",
                        }


def get_data_type(v: str) -> str:
    try:
        result = SUPPORTED_DATA_TYPES[v.lower()]
        kwargs = {}
        if v == "character":
            kwargs['max_length'] = settings.DYNAMIC_MODELS['DEFAULT_CHAR_LENGHT']

        return result, kwargs
    except KeyError:
        raise ValueError(f'Unrecognised type {v.lower()}')


def get_table_name(id: int) -> str:
    return '{}{}'.format(settings.DYNAMIC_MODELS['DYNAMIC_TABLE_PREFIX'], id)