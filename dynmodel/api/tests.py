from django.urls import reverse
from django.db import connection, connections, transaction
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase

from .models import IncrementableSingletonModel
from .utils import unregister_models


class InceremntableSingleton(APITestCase):
    def test_counter(self):
        cnt = IncrementableSingletonModel.load()
        self.assertEqual(cnt.value, 0)
        self.assertEqual(cnt.next(), 1)
        self.assertEqual(cnt.next(), 2)

    def test_reload_counter(self):
        cnt1 = IncrementableSingletonModel.load()
        self.assertEqual(cnt1.value, 0)

        self.assertEqual(cnt1.next(), 1)

        cnt2 = IncrementableSingletonModel.load()
        self.assertEqual(cnt2.value, 1)
        self.assertEqual(cnt2.next(), 2)


"""
All tests are in one method as I'm unable to disable transaction to prevent removeal of new tables
"""
#@override_settings(ROOT_URLCONF='tests.test_atomic_requests')
#@override_settings(ATOMIC_REQUESTS=False)
class DBTransaction(APITestCase):
    create_datamodel = {
        "make": "character",
        "model": "character",
        "year": "integer",
        "valid_license": "boolean"
    }

    update_datamodel = {
        "make": "character",
        "model": "character",
        "make_year": "integer",
        "licence_valid_year": "integer"
    }

    error_datamodel = {
        "make": "character",
        "model": "charcter",
        "make_year": "integer",
        "licence_valid_year": "integer"   
    }

    data = [
        {
            "make": "toyota",
            "model": "corolla",
            "year": 2012,
            "valid_license": False
        },
        {
            "make": "mazda",
            "model": "cx-5",
            "year": 2018,
            "valid_license": True
        }
    ]

    error_data = [
        {
            "make": "mazda",
            "model": "cx-5",
            "year": 2018,
            "valid_license": "Tru"
        },
        {
            "make": "mazda",
            "model": "cx-5",
            "year": "xxx",
            "valid_license": True
        },
    ]
    
    # def setUp(self):
    #     connections.databases['default']['ATOMIC_REQUESTS'] = False

    # def tearDown(self):
    #     connections.databases['default']['ATOMIC_REQUESTS'] = True

    #@override_settings(ATOMIC_REQUESTS=False)
    def test_create_table(self):
        """
        Ensure we can create a new account object.
        """
        create_url = reverse('create-table')
        tables_url = reverse('list-django-tables')
        
        response = self.client.post(create_url, self.error_datamodel, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(create_url, self.create_datamodel, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id1 = response.data['id']

        response = self.client.get(tables_url)
        self.assertEqual(len(response.data), 1)

        response = self.client.post(create_url, self.create_datamodel, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        id2 = response.data['id']

        response = self.client.get(tables_url)
        self.assertEqual(len(response.data), 2)

        create_row_url = reverse('create-row', args=[id2])
        for d in self.data:
            response = self.client.post(create_row_url, d, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        list_rows_url1 = reverse('list-rows', args=[id1])
        response = self.client.get(list_rows_url1)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        list_rows_url2 = reverse('list-rows', args=[id2])
        response = self.client.get(list_rows_url2)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.data))
        self.assertEqual(response.data[0].get("make"), "toyota")
        self.assertEqual(response.data[1].get("make"), "mazda")

        for d in self.error_data:
            response = self.client.post(create_row_url, d, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(create_row_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(create_row_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        list_error_row_url = reverse('list-rows', args=[9999])
        response = self.client.get(list_error_row_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        create_error_row_url = reverse('create-row', args=[9999])
        response = self.client.post(create_error_row_url, self.data[0], format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        update_url = reverse('update-table', args=[id2])

        response = self.client.put(update_url, self.update_datamodel, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.put(update_url, self.error_datamodel, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(tables_url)
        self.assertEqual(len(response.data), 2)

        response = self.client.get(list_rows_url2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.data))
        self.assertEqual(response.data[0].get("make"), "toyota")
        self.assertEqual(response.data[1].get("make"), "mazda")
        self.assertEqual(response.data[0].get('licence_valid_year'), None)


# it's necessary to unregister previous model
# registered on application start before database change done by test
unregister_models()
