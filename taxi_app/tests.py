from rest_framework import status
from rest_framework.test import APITestCase
from .models import *
from django.urls import reverse


class AuthTestCase(APITestCase):
    def login(self, username, password):
        response = self.client.post('http://127.0.0.1:8000/taxiapp/login/',
                                    data={'username': '{}'.format(username), 'password': '{}'.format(password)})
        if response.status_code == 200:
            self.client.credentials(
                HTTP_AUTHORIZATION="Token {}".format(Token.objects.get(user=TaxiUser.objects.get(username=username))))

    fixtures = [r'taxi_app/fixtures/initial_data.json', ]


class DriverTest(AuthTestCase):

    def message(self, curr_status, next_status):
        message = 'session updated from {} to {}'.format(curr_status,next_status)
        return message

    error_message = 'you cant change to this status'
    unauthorized_message = 'you can only update your own work status'

    def setUp(self):
        # super(DriverTest, self).setUp()
        driver = Driver.objects.get(user=3)
        self.login(driver.user.username, 'Pass@123')

    def test_get_driver(self):
        # check getting driver
        driver = Driver.objects.get(user=3)
        response = self.client.get(reverse('taxi_app:driver-detail', args=[1]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_inactive_to_seeking(self):
        # check changing status from inactive to seeking
        message = self.message('inactive', 'seeking')
        driver = Driver.objects.get(user=3)
        driver.change_status(next_status='inactive')
        response = self.client.put('http://127.0.0.1:8000/taxiapp/drivers/{}/change_status/'.format(driver.id),
                                   data={'work_status': 'seeking'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], message)

    def test_seeking_to_inactive(self):
        # check changing status from seeking to inactive
        message = self.message('seeking', 'inactive')
        self.test_inactive_to_seeking()
        driver = Driver.objects.get(user=3)
        driver.change_status(next_status='seeking')
        response = self.client.put('http://127.0.0.1:8000/taxiapp/drivers/{}/change_status/'.format(driver.id),
                                   data={'work_status': 'inactive'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], message)

    def test_seeking_to_intransit(self):
        # check changing status from seeking to in transit

        driver = Driver.objects.get(user=3)
        driver.change_status(next_status='seeking')
        response = self.client.put('http://127.0.0.1:8000/taxiapp/drivers/{}/change_status/'.format(driver.id),
                                   data={'work_status': 'in transit'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['status'], self.error_message)

    def test_intransit_to_seeking(self):
        # check changing status from in transit to seeking
        driver = Driver.objects.get(user=3)
        driver.change_status(next_status='in transit')
        response = self.client.put('http://127.0.0.1:8000/taxiapp/drivers/{}/change_status/'.format(driver.id),
                                   data={'work_status': 'seeking'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['status'], self.error_message)

    def test_intransit_to_inactive(self):
        # check changing status from in transit to inactive
        driver = Driver.objects.get(user=3)
        driver.change_status(next_status='in transit')
        response = self.client.put('http://127.0.0.1:8000/taxiapp/drivers/{}/change_status/'.format(driver.id),
                                   data={'work_status': 'inactive'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['status'], self.error_message)

    def test_inactive_to_intransit(self):
        # check changing status from inactive to in transit
        driver = Driver.objects.get(user=3)
        driver.change_status(next_status='inactive')
        response = self.client.put('http://127.0.0.1:8000/taxiapp/drivers/{}/change_status/'.format(driver.id),
                                   data={'work_status': 'in transit'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['status'], self.error_message)

    def test_change_another_record(self):
        # check changing status for another driver
        driver = Driver.objects.get(id=1)
        driver.change_status(next_status='inactive')
        response = self.client.put('http://127.0.0.1:8000/taxiapp/drivers/2/change_status/',
                                   data={'work_status': 'seeking'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.json()['status'], self.unauthorized_message)

    def test_get_work_hours(self):
        self.test_seeking_to_inactive()
        response = self.client.get('http://127.0.0.1:8000/taxiapp/drivers/1/work_hours/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RequestTest(AuthTestCase):

    def message(self, curr_status, next_status):
        message = 'request has been changed from {} to {}'.format(curr_status,next_status)
        return message

    error_message = 'you cant change to this status'

    def setUp(self):
        # super(RequestTest, self).setUp()
        driver = Driver.objects.get(id=1)
        driver.change_status(next_status='seeking')
        self.login(driver.user.username, 'Pass@123')

    def test_create_request_success(self):
        client = TaxiUser.objects.get(id=5)
        self.login(client.username, 'Pass@123')
        # test creating request
        response = self.client.post('http://127.0.0.1:8000/taxiapp/requests/')
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_request_fail(self):
        # test creating request
        response = self.client.post('http://127.0.0.1:8000/taxiapp/requests/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['detail'], 'Only client can perform this action.')

    def test_create_multiple_request(self):
        # test creating request
        client = TaxiUser.objects.get(id=2)
        self.login(client.username, 'Pass@123')
        response = self.client.post('http://127.0.0.1:8000/taxiapp/requests/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['status'], 'you cannot make multiple requests at the same time')

    def test_delete_request_success(self):
        client = TaxiUser.objects.get(id=2)
        self.login(client.username, 'Pass@123')
        response = self.client.delete('http://127.0.0.1:8000/taxiapp/requests/16/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_request_fail(self):
        client = TaxiUser.objects.get(id=5)
        self.login(client.username, 'Pass@123')
        response = self.client.delete('http://127.0.0.1:8000/taxiapp/requests/17/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['detail'], 'Only retrieve/update/delete records you created')

    def test_new_to_accepted(self):
        # check changing request status from new to accepted
        response = self.client.put('http://127.0.0.1:8000/taxiapp/requests/17/change_status/',
                                   data={'request_status': 'accepted'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], self.message('new', 'accepted'))

    def test_accepted_to_complete(self):
        # check changing request status from accepted to complete
        self.test_new_to_accepted()
        req = Request.objects.get(id=17)
        req.change_status(next_status='accepted')
        response = self.client.put('http://127.0.0.1:8000/taxiapp/requests/17/change_status/',
                                   data={'request_status': 'complete'})
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()['status'], self.message('accepted', 'complete'))

    def test_accepted_to_new(self):
        # check changing request status from accepted to new
        req = Request.objects.get(id=17)
        req.change_status(next_status='accepted')
        response = self.client.put('http://127.0.0.1:8000/taxiapp/requests/17/change_status/',
                                   data={'request_status': 'new'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['status'], self.error_message)

    def test_complete_to_accepted(self):
        # check changing request status from complete to accepted
        req = Request.objects.get(id=17)
        req.change_status(next_status='complete')
        response = self.client.put('http://127.0.0.1:8000/taxiapp/requests/17/change_status/',
                                   data={'request_status': 'accepted'})
        print(response.content)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['status'], self.error_message)

    def test_complete_to_new(self):
        # check changing request status from complete to new
        req = Request.objects.get(id=17)
        req.change_status(next_status='complete')
        response = self.client.put('http://127.0.0.1:8000/taxiapp/requests/17/change_status/',
                                   data={'request_status': 'new'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['status'], self.error_message)

    def test_another(self):
        # check changing request status from new to complete
        driver = Driver.objects.get(id=2)
        self.login(driver.user.username, 'Pass@123')
        req = Request.objects.get(id=17)
        req.change_status(next_status='new')
        response = self.client.put('http://127.0.0.1:8000/taxiapp/requests/17/change_status/',
                                   data={'request_status': 'complete'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['status'], self.error_message)

    def test_get_request_driver(self):
        response = self.client.get('http://127.0.0.1:8000/taxiapp/requests/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_request_admin(self):
        admin = TaxiUser.objects.get(id=1)
        self.login(admin.username, 'Pass@123')
        response = self.client.get('http://127.0.0.1:8000/taxiapp/requests/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_request_client(self):
        client = TaxiUser.objects.get(id=2)
        self.login(client.username, 'Pass@123')
        response = self.client.get('http://127.0.0.1:8000/taxiapp/requests/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['detail'], 'Only driver or admin can perform this action.')


class TaxiTests(AuthTestCase):

    def test_add_taxi_success(self):
        # check adding new taxi by admin
        admin = TaxiUser.objects.get(id=1)
        self.login(username=admin.username, password='Pass@123')
        response = self.client.post('http://127.0.0.1:8000/taxiapp/taxis/', data={"car_model": "mercedes E200",
                                                                                   "num_of_passengers": 5,
                                                                                   "driver": 2})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    #
    # def test_get_taxi(self):
    #     # check adding new taxi by admin
    #     admin = TaxiUser.objects.get(id=1)
    #     self.login(username=admin.username, password='Pass@123')
    #     response = self.client.get(reverse('taxi_app:taxi-detail', args=[1]))
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_one_driver_one_taxi(self):
        admin = TaxiUser.objects.get(id=1)
        self.login(username=admin.username, password='Pass@123')
        response = self.client.post('http://127.0.0.1:8000/taxiapp/taxis/', data={"car_model": "mercedes E200",
                                                                                   "num_of_passengers": 5,
                                                                                   "driver": 1})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.json()['driver'], ['This field must be unique.'])


    def test_add_taxi_fail(self):
        driver = TaxiUser.objects.get(id=3)
        self.login(username=driver.username, password='Pass@123')
        response = self.client.post('http://127.0.0.1:8000/taxiapp/taxis/', data={"car_model": "mercedes E200",
                                                                                   "num_of_passengers": 5,
                                                                                   "driver": 1})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.json()['detail'], 'Only admin can perform this action.')