from django.db import models
from django.contrib.auth.models import AbstractUser
import jwt
from django.conf import settings
from datetime import datetime, timedelta
# Create your models here.

TOKEN_DURATION = 24

class User(AbstractUser):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    dob = models.DateTimeField()
    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=50, blank=True)
    @property
    def token(self):
        token = jwt.encode({'username': self.username, 'exp': datetime.utcnow() + timedelta(hours=TOKEN_DURATION)},
                           settings.SECRET_KEY, algorithm='HS256')
        return token
