from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, URLPatternsTestCase
from rest_framework.test import APIClient
from .models import *
from django.urls import include, path


class DriverTests(APITestCase):

    def test_driver(self):
        user = TaxiUser.objects.create(
            username='testdriver',
            password='test',
            first_name='driver',
            last_name='test',
            email='testemail',
            phone='05987753',
            address='wtvr',
            user_type='driver'
        )
        token = Token.objects.get(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        Driver.objects.create(
            user=user, work_status='inactive')
        driver = Driver.objects.get(user=user)
        response = self.client.get(f'http://127.0.0.1:8000/taxiapp/drivers/{driver.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # check changing status from inactive to seeking
        driver.change_status(next_status='inactive')
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/drivers/{driver.id}/change_status/',
                                   data={'work_status': 'seeking'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check changing status from seeking to inactive
        driver.change_status(next_status='seeking')
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/drivers/{driver.id}/change_status/',
                                   data={'work_status': 'inactive'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check changing status from seeking to in transit
        driver.change_status(next_status='seeking')
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/drivers/{driver.id}/change_status/',
                                   data={'work_status': 'in transit'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # check changing status from in transit to seeking
        driver.change_status(next_status='in transit')
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/drivers/{driver.id}/change_status/',
                                   data={'work_status': 'seeking'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # check changing status from in transit to inactive
        driver.change_status(next_status='in transit')
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/drivers/{driver.id}/change_status/',
                                   data={'work_status': 'inactive'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # check changing status from inactive to in transit
        driver.change_status(next_status='inactive')
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/drivers/{driver.id}/change_status/',
                                   data={'work_status': 'in transit'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_request(self):
        client = TaxiUser.objects.create(
            username='testclient',
            password='test',
            first_name='client',
            last_name='test',
            email='testemail',
            phone='05987753',
            address='wtvr',
            user_type='client'
        )
        token = Token.objects.get(user=client)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        # test creating request
        response = self.client.post(f'http://127.0.0.1:8000/taxiapp/requests/', format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        req = Request.objects.get(client=client)

        user = TaxiUser.objects.create(
            username='testdriver',
            password='test',
            first_name='driver',
            last_name='test',
            email='testemail',
            phone='05987753',
            address='wtvr',
            user_type='driver'
        )
        token = Token.objects.get(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")

        Driver.objects.create(
            user=user, work_status='inactive')
        driver = Driver.objects.get(user=user)

        # check changing request status from new to accepted
        driver.change_status(next_status='seeking')
        req.request_status = 'new'
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/requests/{req.id}/change_status/',
                                   data={'request_status': 'accepted'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check changing request status from new to accepted
        req.request_status = 'accepted'
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/requests/{req.id}/change_status/',
                                   data={'request_status': 'complete'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # check changing request status from new to accepted
        req.request_status = 'accepted'
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/requests/{req.id}/change_status/',
                                   data={'request_status': 'new'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # check changing request status from new to accepted
        req.request_status = 'complete'
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/requests/{req.id}/change_status/',
                                   data={'request_status': 'accepted'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # check changing request status from new to accepted
        req.request_status = 'complete'
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/requests/{req.id}/change_status/',
                                   data={'request_status': 'new'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # check changing request status from new to accepted
        req.request_status = 'new'
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/requests/{req.id}/change_status/',
                                   data={'request_status': 'complete'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
