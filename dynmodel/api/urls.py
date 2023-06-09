from django.urls import path
from . import views

urlpatterns = [
    path('', views.api_root, name='api-list'),
    path('tables/', views.list_tables, name='list-tables'),
    path('django-tables/', views.list_django_tables, name='list-django-tables'),
    path('table/', views.create_table, name='create-table'),
    path('table/<int:id>/', views.update_table, name='update-table'),
    path('table/<int:id>/row/', views.create_row, name='create-row'),
    path('table/<int:id>/rows/', views.list_rows, name='list-rows'),
]

