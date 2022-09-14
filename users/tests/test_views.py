from django.test import TestCase, Client
from django.urls import resolve, reverse
import json
from ..__init__ import *
from ..models import User
from ..serializers import UserSerializer


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

    def test_sign_up_POST(self):
        response = self.client.post(reverse(SIGN_UP_URL), {'username': self.new_username,
                                                           'password': self.new_password,
                                                           'first_name': self.new_first_name,
                                                           'last_name': self.new_last_name,
                                                           'email': self.new_email})
        self.assertEquals(response.status_code, OK_STAT_CODE)

    def test_log_in_POST(self):
        response = self.client.post(reverse(LOG_IN_URL), {'username': self.dummy_username,
                                                          'password': self.dummy_password})
        self.assertEquals(response.status_code, OK_STAT_CODE)

    def test_get_me_post(self):
        response = self.client.post(reverse(GET_ME_URL), {'authToken': self.dummy_jwt})
        self.assertEquals(response.status_code, OK_STAT_CODE)
