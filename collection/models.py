from django.db import models
from users.models import User
from files.models import File
class Collection(models.Model):
    name = models.CharField(max_length=30, primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    num_items = models.IntegerField()
    size = models.IntegerField()
    allFiles = models.ManyToManyField(File, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)