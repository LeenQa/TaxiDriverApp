from rest_framework import status
from rest_framework.test import APITestCase
from .models import *


class AuthTestCase(APITestCase):
    def login(self, username, password):
        response = self.client.post(f'http://127.0.0.1:8000/taxiapp/login/',
                                    data={'username': f'{username}', 'password': f'{password}'}, format='json')
        if response.status_code == 200:
            self.client.credentials(
                HTTP_AUTHORIZATION=f"Token {Token.objects.get(user=TaxiUser.objects.get(username=username))}")

    def setUp(self):
        admin = TaxiUser.objects.create(
            username='testadmin',
            password='test',
            first_name='admin',
            last_name='test',
            email='testemail',
            phone='05987753',
            address='wtvr',
            user_type='admin'
        )
        admin.set_password('test')
        admin.save()
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
        client.set_password('test')
        client.save()
        user_drv = TaxiUser.objects.create(
            username='testdriver',
            password='test',
            first_name='driver',
            last_name='test',
            email='testemail',
            phone='05987753',
            address='wtvr',
            user_type='driver'
        )
        user_drv.set_password('test')
        user_drv.save()
        driver = Driver.objects.create(
            user=user_drv, work_status='inactive')
        user_drv2 = TaxiUser.objects.create(
            username='testdriver2',
            password='test',
            first_name='driver2',
            last_name='test',
            email='testemail',
            phone='05987753',
            address='wtvr',
            user_type='driver'
        )
        user_drv2.set_password('test')
        user_drv2.save()
        driver = Driver.objects.create(
            user=user_drv2, work_status='inactive')

        client2 = TaxiUser.objects.create(
            username='testclient2',
            password='test',
            first_name='client2',
            last_name='test',
            email='testemail',
            phone='05987753',
            address='wtvr',
            user_type='client'
        )
        client2.set_password('test')
        client2.save()


class DriverTest(AuthTestCase):

    def setUp(self):
        super(DriverTest, self).setUp()
        driver = Driver.objects.get(user=3)
        AuthTestCase.login(self, driver.user.username, 'test')

    def test_get_driver(self):
        # check getting driver
        driver = Driver.objects.get(user=3)
        response = self.client.get(f'http://127.0.0.1:8000/taxiapp/drivers/{driver.id}/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_inactive_to_seeking(self):
        # check changing status from inactive to seeking
        driver = Driver.objects.get(user=3)
        driver.change_status(next_status='inactive')
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/drivers/{driver.id}/change_status/',
                                   data={'work_status': 'seeking'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], 'session updated from inactive to seeking')

    def test_seeking_to_inactive(self):
        # check changing status from seeking to inactive
        self.test_inactive_to_seeking()
        driver = Driver.objects.get(user=3)
        driver.change_status(next_status='seeking')
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/drivers/{driver.id}/change_status/',
                                   data={'work_status': 'inactive'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], 'session updated from seeking to inactive')

    def test_seeking_to_intransit(self):
        # check changing status from seeking to in transit
        driver = Driver.objects.get(user=3)
        driver.change_status(next_status='seeking')
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/drivers/{driver.id}/change_status/',
                                   data={'work_status': 'in transit'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['status'], 'you cant change to this status')

    def test_intransit_to_seeking(self):
        # check changing status from in transit to seeking
        driver = Driver.objects.get(user=3)
        driver.change_status(next_status='in transit')
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/drivers/{driver.id}/change_status/',
                                   data={'work_status': 'seeking'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['status'], 'you cant change to this status')

    def test_intransit_to_inactive(self):
        # check changing status from in transit to inactive
        driver = Driver.objects.get(user=3)
        driver.change_status(next_status='in transit')
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/drivers/{driver.id}/change_status/',
                                   data={'work_status': 'inactive'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['status'], 'you cant change to this status')

    def test_inactive_to_intransit(self):
        # check changing status from inactive to in transit
        driver = Driver.objects.get(user=3)
        driver.change_status(next_status='inactive')
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/drivers/{driver.id}/change_status/',
                                   data={'work_status': 'in transit'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['status'], 'you cant change to this status')

    def test_change_another_record(self):
        # check changing status for another driver
        driver = Driver.objects.get(id=1)
        driver.change_status(next_status='inactive')
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/drivers/2/change_status/',
                                   data={'work_status': 'seeking'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['status'], 'you can only update your own work status')

    def test_get_work_hours(self):
        self.test_seeking_to_inactive()
        response = self.client.get(f'http://127.0.0.1:8000/taxiapp/drivers/1/work_hours/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RequestTest(AuthTestCase):

    def setUp(self):
        super(RequestTest, self).setUp()
        driver = Driver.objects.get(id=1)
        driver.change_status(next_status='seeking')
        client = TaxiUser.objects.get(id=2)
        Request.objects.create(client=client, request_status='new', driver=driver)
        AuthTestCase.login(self, driver.user.username, 'test')

    def test_create_request_success(self):
        client = TaxiUser.objects.get(id=5)
        AuthTestCase.login(self, client.username, 'test')
        # test creating request
        response = self.client.post(f'http://127.0.0.1:8000/taxiapp/requests/', format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_request_fail(self):
        # test creating request
        response = self.client.post(f'http://127.0.0.1:8000/taxiapp/requests/', format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['detail'], 'Only client can perform this action.')

    def test_create_multiple_request(self):
        # test creating request
        client = TaxiUser.objects.get(id=2)
        AuthTestCase.login(self, client.username, 'test')
        response = self.client.post(f'http://127.0.0.1:8000/taxiapp/requests/', format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['status'], 'you cannot make multiple requests at the same time')

    def test_delete_request_success(self):
        client = TaxiUser.objects.get(id=2)
        AuthTestCase.login(self, client.username, 'test')
        response = self.client.delete(f'http://127.0.0.1:8000/taxiapp/requests/1/', format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_request_fail(self):
        client = TaxiUser.objects.get(id=5)
        AuthTestCase.login(self, client.username, 'test')
        response = self.client.delete(f'http://127.0.0.1:8000/taxiapp/requests/1/', format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['detail'], 'Only retrieve/update/delete records you created')

    def test_new_to_accepted(self):
        # check changing request status from new to accepted
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/requests/1/change_status/',
                                   data={'request_status': 'accepted'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], 'request has been changed from new to accepted')

    def test_accepted_to_complete(self):
        # check changing request status from accepted to complete
        self.test_new_to_accepted()
        req = Request.objects.get(id=1)
        req.change_status(next_status='accepted')
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/requests/1/change_status/',
                                   data={'request_status': 'complete'}, format='json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], 'request has been changed from accepted to complete')

    def test_accepted_to_new(self):
        # check changing request status from accepted to new
        req = Request.objects.get(id=1)
        req.change_status(next_status='accepted')
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/requests/1/change_status/',
                                   data={'request_status': 'new'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['status'], 'you cant change from accepted to new')

    def test_complete_to_accepted(self):
        # check changing request status from complete to accepted
        req = Request.objects.get(id=1)
        req.change_status(next_status='complete')
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/requests/1/change_status/',
                                   data={'request_status': 'accepted'}, format='json')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['status'], 'you cant change from complete to accepted')

    def test_complete_to_new(self):
        # check changing request status from complete to new
        req = Request.objects.get(id=1)
        req.change_status(next_status='complete')
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/requests/1/change_status/',
                                   data={'request_status': 'new'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['status'], 'you cant change from complete to new')

    def test_another(self):
        # check changing request status from new to complete
        driver = Driver.objects.get(id=2)
        AuthTestCase.login(self, driver.user.username, 'test')
        req = Request.objects.get(id=1)
        req.change_status(next_status='new')
        response = self.client.put(f'http://127.0.0.1:8000/taxiapp/requests/1/change_status/',
                                   data={'request_status': 'complete'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['status'], 'you cant change from new to complete')

    def test_get_request_driver(self):
        response = self.client.get(f'http://127.0.0.1:8000/taxiapp/requests/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_request_driver(self):
        admin = TaxiUser.objects.get(id=1)
        AuthTestCase.login(self, admin.username, 'test')
        response = self.client.get(f'http://127.0.0.1:8000/taxiapp/requests/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_request_client(self):
        client = TaxiUser.objects.get(id=2)
        AuthTestCase.login(self, client.username, 'test')
        response = self.client.get(f'http://127.0.0.1:8000/taxiapp/requests/', format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['detail'], 'Only driver or admin can perform this action.')


class TaxiTests(AuthTestCase):

    def test_add_taxi_success(self):
        admin = TaxiUser.objects.get(id=1)
        AuthTestCase.login(self, username=admin.username, password='test')
        response = self.client.post(f'http://127.0.0.1:8000/taxiapp/taxis/', data={"car_model": "mercedes E200",
                                                                                   "num_of_passengers": 5,
                                                                                   "driver": 1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_one_driver_one_taxi(self):
        admin = TaxiUser.objects.get(id=1)
        AuthTestCase.login(self, username=admin.username, password='test')
        response = self.client.post(f'http://127.0.0.1:8000/taxiapp/taxis/', data={"car_model": "mercedes E200",
                                                                                   "num_of_passengers": 5,
                                                                                   "driver": 1}, format='json')

        response = self.client.post(f'http://127.0.0.1:8000/taxiapp/taxis/', data={"car_model": "mercedes E200",
                                                                                   "num_of_passengers": 5,
                                                                                   "driver": 1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['driver'], ['This field must be unique.'])

    def test_add_taxi_fail(self):
        driver = TaxiUser.objects.get(id=3)
        AuthTestCase.login(self, username=driver.username, password='test')
        response = self.client.post(f'http://127.0.0.1:8000/taxiapp/taxis/', data={"car_model": "mercedes E200",
                                                                                   "num_of_passengers": 5,
                                                                                   "driver": 1}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['detail'], 'Only admin can perform this action.')
