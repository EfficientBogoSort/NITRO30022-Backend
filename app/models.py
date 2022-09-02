from django.db import models

class File(models.Model):
    name = models.CharField(max_length=100)
    submit_date = models.DateTimeField(auto_now_add=True)
    file_src = models.FileField()



# Create your models here.
class Collection(models.Model):
    name = models.CharField(max_length=100)
    files = models.ManyToManyField(File)
    creation_date = models.DateTimeField(auto_now_add=True)

