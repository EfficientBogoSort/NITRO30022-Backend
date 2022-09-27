import json

from django.test import TestCase, Client
from django.urls import resolve, reverse
import jwt
from django.conf import settings
from ..__init__ import *
from users.__init__ import *
from datetime import datetime, timedelta
from ..views import CollectionViewSet


class TestView(TestCase):

    def setUp(self):
        self.client = Client()
        self.dummy_username = 'John123'
        self.collections_list = reverse(COLLECTION_URL + '-list')
        self.dummy_account = self.client.post(reverse(SIGN_UP_URL), {'username': self.dummy_username,
                                                                     'password': 'pwd123',
                                                                     'email': 'dummy@gg.com'})
        self.dummy_jwt = self.dummy_account.json().get('token')
        self.dummy_collection_name = 'photos'
        self.client.post(self.collections_list, {'authToken': self.dummy_jwt,
                                                 'name': self.dummy_collection_name})
        self.fake_username = 'Deadpool'
    def test_get_all_collns_status_200(self):
        response = self.client.get(self.collections_list, {'authToken': self.dummy_jwt})
        self.assertEquals(response.status_code, OK_STAT_CODE)

    def test_get_all_collns_exists(self):
        response = self.client.get(self.collections_list, {'authToken': self.dummy_jwt})
        response_data = json.loads(response.content.decode())
        if len(response_data) == 0:
            return False
        colln = response_data[0]
        self.assertEquals((colln['name'], colln['num_items'], colln['size'], colln['owner'], colln['files']),
                          (self.dummy_collection_name, 0, 0, self.dummy_username, []))

    def test_create_existing_colln(self):
        response = self.client.post(self.collections_list, {'authToken': self.dummy_jwt,
                                                            'name': self.dummy_collection_name})
        self.assertEquals(response.status_code, INVALID_DATA_CODE)

    def test_create_colln_unexisting_user(self):
        fake_token = jwt.encode({'username': self.fake_username, 'exp': datetime.utcnow() + timedelta(hours=1)},
                                settings.SECRET_KEY, algorithm='HS256')
        response = self.client.post(self.collections_list, {'authToken': fake_token})
        self.assertEquals(response.status_code, INVALID_DATA_CODE)

    def test_get_all_success(self):
        response = self.client.get(self.collections_list, {'authToken': self.dummy_jwt})
        self.assertEquals(OK_STAT_CODE, response.status_code)

    def test_get_all_unexisting_user(self):
        fake_token = jwt.encode({'username': self.fake_username, 'exp': datetime.utcnow() + timedelta(hours=1)},
                                settings.SECRET_KEY, algorithm='HS256')
        response = self.client.get(self.collections_list, {'authToken': fake_token})
        self.assertEquals(response.status_code, INVALID_DATA_CODE)

    def test_retrieve_success(self):
        request = reverse(COLLECTION_URL + '-detail', kwargs={'pk': self.dummy_collection_name})
        response = self.client.get(request, {'authToken': self.dummy_jwt})
        self.assertEquals(OK_STAT_CODE, response.status_code)

    def test_retrieve_no_found(self):
        request = reverse(COLLECTION_URL + '-detail', kwargs={'pk': 'videos'})
        response = self.client.get(request, {'authToken': self.dummy_jwt})
        self.assertEquals(NOT_FOUND, response.status_code)

    def test_destroy_success(self):
        new_colln_name = 'notes'
        a = self.client.post(self.collections_list, {'authToken': self.dummy_jwt,
                                                     'name': new_colln_name})

        request = reverse(COLLECTION_URL + '-detail', kwargs={'pk': new_colln_name})
        response = self.client.delete(request)
        self.assertEquals(OK_STAT_CODE, response.status_code)

    def test_updt_success(self):
        updt_name = 'Photos'
        request = reverse(COLLECTION_URL + '-detail', kwargs={'pk': updt_name})
        response = self.client.put(request)
        self.assertEquals(OK_STAT_CODE, response.status_code)
