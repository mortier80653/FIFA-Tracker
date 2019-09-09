from django.urls import resolve, reverse
from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework import status


class AccountLoginTests(APITestCase):
    def setUp(self):
        self.data = {
            'username': "TestLogin",
            'email': "TestLogin@fifatracker.net",
            'password': "TestLoginPassword123456!@#",
        }
        self.client.post(reverse('api:user_create'), self.data, format='json')

        self.data.pop('email', None)
        self.login_url = reverse('api:user_login')

    def test_login_inactive(self):
        response = self.client.post(self.login_url, self.data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], 'account_not_active')

    def test_login_user_wrong_password(self):
        user = User.objects.get()
        user.is_active = True
        user.save()

        data = {
            'username': self.data['username'],
            'password': '123'
        }

        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 'invalid_credentials')

        user.is_active = False
        user.save()

    def test_login_user_not_exist(self):
        data = {
            'username': "estLogin",
            'password': "TestLoginPassword123456!@#",
        }
        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 'invalid_credentials')

    def test_login(self):
        user = User.objects.get()
        user.is_active = True
        user.save()

        response = self.client.post(self.login_url, self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('access' in response.data, True)
        self.assertEqual('refresh' in response.data, True)

        user.is_active = False
        user.save()


class AccountCreateTests(APITestCase):
    def setUp(self):
        self.create_url = reverse('api:user_create')

    def test_create_account(self):
        data = {
            'username': "TestAccCreate",
            'email': "TestAccCreate@fifatracker.net",
            'password': "TestAccCreatePassword123456!@#",
        }
        response = self.client.post(self.create_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'TestAccCreate')
        self.assertFalse('password' in response.data)
        self.assertFalse(User.objects.get().is_active)

    def test_create_account_fake_is_active(self):
        data = {
            'username': "TestAccCreate",
            'email': "TestAccCreate@fifatracker.net",
            'password': "TestAccCreatePassword123456!@#",
            'is_active': True,
        }
        response = self.client.post(self.create_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'TestAccCreate')
        self.assertFalse('password' in response.data)
        self.assertFalse(User.objects.get().is_active)

    def test_create_user_unique_email(self):
        data = {
            'username': "TestAccCreate",
            'email': "TestAccCreate@fifatracker.net",
            'password': "TestAccCreatePassword123456!@#",
        }
        self.client.post(self.create_url, data, format='json')

        data = {
            'username': "TestAccCreate2",
            'email': "TestAccCreate@fifatracker.net",
            'password': "TestAccCreatePassword123456!@#",
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['email']), 1)
        self.assertEqual(response.data['email'][0].code, 'unique')

        data = {
            'username': "TestAccCreate2",
            'email': "testAccCreate@fifatracker.net",
            'password': "TestAccCreatePassword123456!@#",
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['email']), 1)
        self.assertEqual(response.data['email'][0].code, 'unique')

    def test_create_user_unique_gmail(self):
        data = {
            'username': "TestAccCreate",
            'email': "AranaktuFifaTracker@gmail.com",
            'password': "TestAccCreatePassword123456!@#",
        }
        self.client.post(self.create_url, data, format='json')

        data = {
            'username': "TestAccCreate2",
            'email': "Aranaktu.FifaTracker@gmail.com",
            'password': "TestAccCreatePassword123456!@#",
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['email']), 1)
        self.assertEqual(response.data['email'][0].code, 'unique')

        data = {
            'username': "TestAccCreate2",
            'email': "AranaktuF.ifaTra.ck.er@gmail.com",
            'password': "TestAccCreatePassword123456!@#",
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['email']), 1)
        self.assertEqual(response.data['email'][0].code, 'unique')

    def test_create_user_unique_username(self):
        data = {
            'username': "TestAccCreate",
            'email': "TestAccCreate@fifatracker.net",
            'password': "TestAccCreatePassword123456!@#",
        }
        self.client.post(self.create_url, data, format='json')

        data = {
            'username': "TestAccCreate",
            'email': "TestAccCreate2@fifatracker.net",
            'password': "TestAccCreatePassword123456!@#",
        }
        response = self.client.post(self.create_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['username']), 1)
        self.assertEqual(response.data['username'][0].code, 'unique')

        data = {
            'username': "testAccCreate",
            'email': "TestAccCreate2@fifatracker.net",
            'password': "TestAccCreatePassword123456!@#",
        }
        response = self.client.post(self.create_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(response.data['username']), 1)
        self.assertEqual(response.data['username'][0].code, 'unique')

    def test_create_user_with_short_password(self):
        data = {
            'username': "TestAccCreate",
            'email': "TestAccCreate@fifatracker.net",
            'password': "123",
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(len(response.data['password']), 1)
        self.assertEqual(response.data['password'][0].code, 'min_length')

    def test_create_user_with_no_password(self):
        data = {
            'username': "TestAccCreate",
            'email': "TestAccCreate@fifatracker.net",
            'password': "",
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.count(), 0)
        self.assertEqual(len(response.data['password']), 1)
        self.assertEqual(response.data['password'][0].code, 'blank')
