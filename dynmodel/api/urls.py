from django.urls import path
#from rest_framework.urlpatterns import format_suffix_patterns
from .views import api_root, create_table, update_table, create_row, list_rows, list_tables

urlpatterns = [
    path('', api_root, name='api-list'),
    path('tables/', list_tables, name='list-tables'),
    path('table/', create_table, name='create-table'),
    path('table/<int:id>/', update_table, name='update-table'),
    path('table/<int:id>/row/', create_row, name='create-row'),
    path('table/<int:id>/rows/', list_rows, name='list-rows'),
]

