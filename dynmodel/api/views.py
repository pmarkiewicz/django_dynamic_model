from importlib import reload, import_module

from django.conf import settings
from django.db import connections
from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.urls import clear_url_caches
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.decorators import parser_classes
from rest_framework.parsers import JSONParser

from dynamic_models.models import ModelSchema, FieldSchema

from .utils import get_data_type, get_table_name
from .serializers import generic_serializer
from .models import IncrementableSingletonModel


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'update table': reverse('update-table', request=request, args=[1]),
        'create table': reverse('create-table', request=request, format=format),
        'create row': reverse('create-row', request=request, format=format, args=[1]),
        'list rows': reverse('list-rows', request=request, format=format, args=[1]),
        'list tables': reverse('list-tables', request=request, format=format),
        'list django tables': reverse('list-django-tables', request=request, format=format),
    })


@api_view(['POST'])
@parser_classes([JSONParser])
def create_table(request):
    """
    Creates table from json file with 'name': 'type' pairs.
    Allowed types: 'boolean', 'character', 'integer'
    Example:

    {
        "make": "character",
        "model": "character",
        "year": "integer",
        "valid_license": "boolean"
    }

    """
   
    if not request.data:
        return Response({'error': 'datamodel cannot be empty'}, status=400)
        
    counter = IncrementableSingletonModel.load()
    id = counter.next()

    table_name = get_table_name(id)
    schema = ModelSchema.objects.create(name=table_name)

    try:
        for name, fld_type in request.data.items():
            cls, kw = get_data_type(fld_type)
            FieldSchema.objects.create(
                name=name,
                model_schema=schema,
                class_name=cls,
                kwargs=kw
            )
    except ValueError as exc:
        schema.delete()
        return Response({'error': str(exc)}, status=400)

    # create model
    reg_model = schema.as_model()
    admin.site.register(reg_model)

    # do we need what is below?
    reload(import_module(settings.ROOT_URLCONF))
    clear_url_caches()

    return Response({'id': id}, status=201)


@api_view(['PUT'])
@parser_classes([JSONParser])
def update_table(request, id):
    """
    Updates dynamic model table from json file with 'name': 'type' pairs.
    Allowed types: 'boolean', 'character', 'integer'
    Example:

    {
        "make": "character",
        "model": "character",
        "make_year": "integer",
        "licence_valid_year": "integer"
    }

    """
    table_name = get_table_name(id)

    try:
        schema = ModelSchema.objects.get(name=table_name)
    except ObjectDoesNotExist:
        return Response({'error': f'invalid model id: {id}'}, status=404)

    try:
        for name, fld_type in request.data.items():
            cls, kw = get_data_type(fld_type)
            FieldSchema.objects.update_or_create(
                name=name,
                model_schema=schema,
                class_name=cls,
                kwargs=kw
            )
    except ValueError as exc:
        return Response({'error': str(exc)}, status=400)

    # create model
    reg_model = schema.as_model()
    try:
        admin.site.unregister(reg_model)
    except NotRegistered:
        # ignore exception, maybe unregister is not needed?
        pass

    admin.site.register(reg_model)
    reload(import_module(settings.ROOT_URLCONF))
    clear_url_caches()

    return Response({'id': id})


@api_view(['POST'])
@parser_classes([JSONParser])
def create_row(request, id):
    """"
    Example:
    {
        "make": "toyota",
        "model": "corolla",
        "year": 2012,
        "valid_license": true
    }
    """
    if not request.data:
        return Response({'error': 'No data'}, status=400)
    
    table_name = get_table_name(id)

    try:
        model = ModelSchema.objects.get(name=table_name).as_model()
    except ObjectDoesNotExist:
        return Response({'error': f'invalid model id: {id}'}, status=404)

    serializer_cls = generic_serializer(model)
    serializer = serializer_cls(data=request.data)
    

    if serializer.is_valid():
        obj = serializer.save()
        return Response({'id': obj.id}, status=201)
    
    return Response({'error': serializer.errors}, status=400)
    
    

    


@api_view(['GET'])
def list_rows(request, id):
    table_name = get_table_name(id)
    try:
        model = ModelSchema.objects.get(name=table_name).as_model()
    except ObjectDoesNotExist:
        return Response({'error': f'invalid model id: {id}'}, status=404)

    serializer_cls = generic_serializer(model)
    rows = model.objects.all()
    serializer = serializer_cls(rows, many=True)

    return Response(serializer.data)


def _get_dyn_tables_prefix() -> str:
    return '{}_{}'.format('dynamic_models', settings.DYNAMIC_MODELS['DYNAMIC_TABLE_PREFIX'])


@api_view(['GET'])
def list_tables(request):
    """
    List of dynamically created tables. Works only with Postresql. Yes it can be done with django.
    """
    filter = _get_dyn_tables_prefix()

    conn = connections['default']

    with conn.cursor() as cursor:
        cursor.execute("""SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                            AND table_type = 'BASE TABLE'
                            AND table_name LIKE '{}%';"""
                        .format(filter))

        table_list = cursor.fetchall()

    return Response(table_list)


@api_view(['GET'])
def list_django_tables(request):
    conn = connections['default']
    table_list = conn.introspection.table_names()
    filter = _get_dyn_tables_prefix()

    return Response([table for table in table_list if table.startswith(filter)])
