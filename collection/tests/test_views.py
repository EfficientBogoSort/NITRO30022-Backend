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
        self.token_header = {'HTTP_AUTHORIZATION': f'Bearer {self.dummy_jwt}'}
        self.dummy_collection_name = 'photos'
        self.client.post(self.collections_list, {'name': self.dummy_collection_name}, **self.token_header)
        self.fake_username = 'Deadpool'
        self.fake_token = jwt.encode({'username': self.fake_username, 'exp': datetime.utcnow() + timedelta(hours=1)},
                                     settings.SECRET_KEY, algorithm='HS256')
        self.invalid_token_header = {'HTTP_AUTHORIZATION': f'Bearer AAAAAAAAAAAAAAAAa'}
        self.fake_token_header = {'HTTP_AUTHORIZATION': f'Bearer {self.fake_token}'}
        self.updated_colln_name = 'Photos'

    # Tests for the list (get all) endpoint
    def test_get_all_collns_status_200(self):
        response = self.client.get(self.collections_list, **self.token_header)
        self.assertEquals(response.status_code, OK_STAT_CODE)

    def test_get_all_collns_exists(self):
        response = self.client.get(self.collections_list, **self.token_header)
        response_data = json.loads(response.content.decode())
        colln = response_data[0]
        self.assertEquals((colln['name'], colln['num_items'], colln['size'], colln['owner'], colln['allFiles']),
                          (self.dummy_collection_name, 0, 0, self.dummy_username, []))

    def test_get_all_cllns_missing_token(self):
        response = self.client.get(self.collections_list)
        self.assertEquals(response.status_code, BAD_REQ_CODE)

    def test_get_all_non_existent_user(self):
        response = self.client.get(self.collections_list, **self.fake_token_header)
        self.assertEquals(response.status_code, NOT_FOUND)

    # Tests for creating a new collection
    def test_create_existing_colln(self):
        response = self.client.post(self.collections_list, {'name': self.dummy_collection_name}, **self.token_header)
        self.assertEquals(response.status_code, INVALID_DATA_CODE)

    def test_create_colln_non_existing_user(self):
        response = self.client.post(self.collections_list, **self.fake_token_header)
        self.assertEquals(response.status_code, NOT_FOUND)

    def test_create_colln_invalid_token(self):
        response = self.client.post(self.collections_list, **self.invalid_token_header)
        self.assertEquals(response.status_code, INVALID_DATA_CODE)

    # Tests for retrieving a collection
    def test_retrieve_success(self):
        request = reverse(COLLECTION_URL + '-detail', kwargs={'pk': self.dummy_collection_name})
        response = self.client.get(request, **self.token_header)
        self.assertEquals(OK_STAT_CODE, response.status_code)

    def test_retrieve_no_found(self):
        request = reverse(COLLECTION_URL + '-detail', kwargs={'pk': 'videos'})
        response = self.client.get(request, **self.token_header)
        self.assertEquals(NOT_FOUND, response.status_code)

    def test_retrieve_invalid_token(self):
        request = reverse(COLLECTION_URL + '-detail', kwargs={'pk': self.dummy_collection_name})
        response = self.client.get(request, **self.invalid_token_header)
        self.assertEquals(response.status_code, INVALID_DATA_CODE)

    def test_retrieve_non_existent_user(self):
        request = reverse(COLLECTION_URL + '-detail', kwargs={'pk': self.dummy_collection_name})
        response = self.client.get(request, **self.fake_token_header)
        self.assertEquals(response.status_code, NOT_FOUND)

    # Tests for the destroy endpoint
    def test_destroy_success(self):
        new_colln_name = 'notes'
        self.client.post(self.collections_list, {'name': new_colln_name}, **self.token_header)

        request = reverse(COLLECTION_URL + '-detail', kwargs={'pk': new_colln_name})
        response = self.client.delete(request, **self.token_header)
        self.assertEquals(OK_STAT_CODE, response.status_code)

    def test_destroy_invalid_token(self):
        # pk choice does not matter here
        request = reverse(COLLECTION_URL + '-detail', kwargs={'pk': 'aa'})

        response = self.client.delete(request, **self.invalid_token_header)
        self.assertEquals(response.status_code, INVALID_DATA_CODE)

    def test_destroy_non_existent_colln(self):
        request = reverse(COLLECTION_URL + '-detail', kwargs={'pk': 'aa'})
        response = self.client.delete(request, **{'HTTP_AUTHORIZATION': f'Bearer {self.dummy_jwt}'})
        self.assertEquals(response.status_code, NOT_FOUND)

    def test_destroy_missing_token(self):
        # pk choice does not matter here
        request = reverse(COLLECTION_URL + '-detail', kwargs={'pk': 'aa'})
        response = self.client.delete(request)
        self.assertEquals(response.status_code, BAD_REQ_CODE)

    def test_destroy_non_existent_user(self):
        # pk choice does not matter here
        request = reverse(COLLECTION_URL + '-detail', kwargs={'pk': 'aa'})
        response = self.client.delete(request, **self.fake_token_header)
        self.assertEquals(response.status_code, NOT_FOUND)

    # Tests for the update endpoint
    def test_updt_success(self):
        request = reverse(COLLECTION_URL + '-detail', kwargs={'pk': self.dummy_collection_name})
        response = self.client.put(request, {'name': self.updated_colln_name}, content_type='application/json',
                                   **self.token_header)
        self.assertEquals(OK_STAT_CODE, response.status_code)

    def test_updt_missing_token(self):
        # pk choice does not matter here
        request = reverse(COLLECTION_URL + '-detail', kwargs={'pk': 'aa'})
        response = self.client.put(request, {'name': self.updated_colln_name}, content_type='application/json')
        self.assertEquals(response.status_code, BAD_REQ_CODE)

    def test_updt_invalid_token(self):
        # pk choice does not matter here
        request = reverse(COLLECTION_URL + '-detail', kwargs={'pk': 'aa'})
        response = self.client.put(request, {'name': self.updated_colln_name}, content_type='application/json',
                                   **self.invalid_token_header)
        self.assertEquals(response.status_code, INVALID_DATA_CODE)

    def test_updt_non_existent_user(self):
        # pk choice does not matter here
        request = reverse(COLLECTION_URL + '-detail', kwargs={'pk': 'aa'})
        response = self.client.put(request, {'name': self.updated_colln_name}, content_type='application/json',
                                   **self.fake_token_header)
        self.assertEquals(response.status_code, NOT_FOUND)

    def test_updt_non_existent_colln(self):
        request = reverse(COLLECTION_URL + '-detail', kwargs={'pk': 'aa'})
        response = self.client.put(request, {'name': self.updated_colln_name}, content_type='application/json',
                                   **self.token_header)
        self.assertEquals(response.status_code, NOT_FOUND)
