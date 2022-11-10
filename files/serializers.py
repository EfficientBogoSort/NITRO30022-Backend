from rest_framework import serializers
from .models import File

class FileSerializer(serializers.ModelSerializer):
    """
    Serializer class for the File model
    """
    class Meta:
        """
        Contains metadata about the serializer
        """
        model = File
        fields = '__all__'