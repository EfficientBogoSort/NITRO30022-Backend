from django.test import TestCase, Client
from django.urls import resolve, reverse
import json
from ..__init__ import *
import jwt
from datetime import timedelta, datetime
from django.conf import settings


class TestView(TestCase):

    def setUp(self):
        self.client = Client()
        self.new_username = 'jhon123'
        self.new_password = 'smith123'
        self.new_first_name = 'John'
        self.new_last_name = 'smith123'
        self.new_email = 'j@s.com'

        self.dummy_username = 'sue123'
        self.dummy_password = 'db123'
        self.dummy_first_name = 'Sue'
        self.dummy_last_name = 'Dearbone'
        self.dummy_email = 's@d.com'
        a = self.client.post(reverse(SIGN_UP_URL), {'username': self.dummy_username,
                                                    'password': self.dummy_password,
                                                    'first_name': self.dummy_first_name,
                                                    'last_name': self.dummy_last_name,
                                                    'email': self.dummy_email})
        self.dummy_jwt = a.json()['token']
        print(a.json().items())
        self.login_url = reverse(LOG_IN_URL)
        self.signup_url = reverse(SIGN_UP_URL)
        self.get_me_url = reverse(GET_ME_URL)
        self.fake_username = 'Bob'

    def test_sign_up_success(self):
        response = self.client.post(self.signup_url, {'username': self.new_username,
                                                      'password': self.new_password,
                                                      'first_name': self.new_first_name,
                                                      'last_name': self.new_last_name,
                                                      'email': self.new_email})
        self.assertEquals(response.status_code, OK_STAT_CODE)

    def test_sign_up_missing_fields(self):
        response = self.client.post(self.signup_url, {'username': self.new_username})
        self.assertEquals(response.status_code, BAD_REQ_CODE)

    def test_sign_up_existing_user(self):
        response = self.client.post(self.signup_url, {'username': self.dummy_username,
                                                      'password': self.dummy_password,
                                                      'first_name': self.dummy_first_name,
                                                      'last_name': self.dummy_last_name,
                                                      'email': self.dummy_email})
        self.assertEquals(response.status_code, INVALID_DATA_CODE)

    def test_log_in_success(self):
        response = self.client.post(self.login_url, {'username': self.dummy_username,
                                                     'password': self.dummy_password})
        self.assertEquals(response.status_code, OK_STAT_CODE)

    def test_log_in_incorrect_password(self):
        response = self.client.post(self.login_url, {'username': self.dummy_username,
                                                     'password': 'abc'})
        self.assertEquals(response.status_code, INVALID_DATA_CODE)

    def test_log_in_incorrect_username(self):
        response = self.client.post(self.login_url, {'username': 'aa',
                                                     'password': 'abc'})
        self.assertEquals(response.status_code, INVALID_DATA_CODE)

    def test_get_me_success(self):
        response = self.client.post(self.get_me_url, {'authToken': self.dummy_jwt})
        self.assertEquals(response.status_code, OK_STAT_CODE)

    def test_get_me_no_token(self):
        response = self.client.post(self.get_me_url)
        self.assertEquals(response.status_code, BAD_REQ_CODE)

    def test_get_me_user_not_found(self):
        token = jwt.encode({'username': self.fake_username, 'exp': datetime.utcnow() + timedelta(hours=24)},
                           settings.SECRET_KEY, algorithm='HS256')
        response = self.client.post(self.get_me_url, {'authToken': token})
        self.assertEquals(response.status_code, NOT_FOUND)

    def test_get_me_tok_expired(self):
        token = jwt.encode({'username': self.dummy_username, 'exp': datetime.utcnow() - timedelta(hours=25)},
                           settings.SECRET_KEY, algorithm='HS256')

        response = self.client.post(self.get_me_url, {'authToken': token})
        self.assertEquals(response.status_code, INVALID_DATA_CODE)
