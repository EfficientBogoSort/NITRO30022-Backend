from django.db import models
from django.contrib.auth.models import AbstractUser
import jwt
from django.conf import settings
from datetime import datetime, timedelta
# Create your models here.

TOKEN_DURATION = 24

class User(AbstractUser):
    """
    Class used to represent a user by django
    """
    email = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=50, blank=True)
    username = models.CharField(max_length=50, primary_key=True)
    friends = models.ManyToManyField('self', blank=True)

    # token used for authentication
    @property
    def token(self):
        """
        Parameters: None
        
        Return: returns a SHA256 encoded JWT token which contains the username, and the expiry time
        """
        token = jwt.encode({'username': self.username, 'exp': datetime.utcnow() + timedelta(hours=TOKEN_DURATION)},
                           settings.SECRET_KEY, algorithm='HS256')
        return token
