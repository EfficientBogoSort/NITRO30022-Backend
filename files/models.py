from django.db import models
 
class File(models.Model):
    title = models.CharField(max_length=30, primary_key=True)
    document = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    class Meta:
        verbose_name_plural = 'Files'