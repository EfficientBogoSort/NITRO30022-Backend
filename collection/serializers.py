from rest_framework import serializers
from collection.models import Collection

class CollectionSerlializer(serializers.ModelSerializer):
    
    class Meta:
        model = Collection
        fields = '__all__'