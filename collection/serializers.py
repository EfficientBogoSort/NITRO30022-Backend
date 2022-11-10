from rest_framework import serializers
from collection.models import Collection

class CollectionSerializer(serializers.ModelSerializer):
    """
    Serializer class for the Collection model
    """
    class Meta:
        """
        Contains metadata about the serializer
        """
        model = Collection
        fields = '__all__'