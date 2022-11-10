from django.db import models
from users.models import User
import uuid
class File(models.Model):
    """
    Class used to represent a file
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=30)
    colln = models.ForeignKey('collection.Collection', on_delete=models.CASCADE)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    document = models.FileField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        verbose_name_plural = 'Files'