from django.db import models
from users.models import User

class Collection(models.Model):
    name = models.CharField(max_length=30)
    owner = models.ManyToOneRel(User)
    size = models.IntegerField
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)