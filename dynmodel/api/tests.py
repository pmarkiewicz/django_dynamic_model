from django.urls import reverse
from django.db import connection, connections, transaction
from django.test import override_settings
from rest_framework import status
from rest_framework.test import APITestCase


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

    data = [
        {
            "make": "toyota",
            "model": "corolla",
            "year": 2012,
            "valid_license": True
        },
        {
            "make": "mazda",
            "model": "cx-5",
            "year": 2018,
            "valid_license": True
        }
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
            print(response)
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

        update_url = reverse('update-table', args=[id2])

        response = self.client.put(update_url, self.update_datamodel, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(tables_url)
        self.assertEqual(len(response.data), 2)

        response = self.client.get(list_rows_url2)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), len(self.data))
        self.assertEqual(response.data[0].get("make"), "toyota")
        self.assertEqual(response.data[1].get("make"), "mazda")
        self.assertEqual(response.data[0].get('licence_valid_year'), None)
