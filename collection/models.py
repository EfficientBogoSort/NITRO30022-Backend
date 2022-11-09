from django.db import models
from users.models import User
from files.models import File
import uuid
class Collection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=30)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    num_items = models.IntegerField()
    size = models.IntegerField()
    private = models.CharField(max_length=10)
    allFiles = models.ManyToManyField(File, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)