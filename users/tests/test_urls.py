from django.test import SimpleTestCase
from django.urls import reverse, resolve
from ..views import *
from ..__init__ import *
class TestUrls(SimpleTestCase):
    def test_log_in_resolved(self):
        url = reverse(LOG_IN_URL)
        self.assertEquals(resolve(url).func.view_class, LogInView)
    def test_sign_ip_resolved(self):
        url = reverse(SIGN_UP_URL)
        self.assertEquals(resolve(url).func.view_class, RegisterView)
    def test_get_me_resolved(self):
        url = reverse(GET_ME_URL)
        self.assertEquals(resolve(url).func, get_user)