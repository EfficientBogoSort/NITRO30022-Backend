
from collection.models import Collection
from rest_framework import viewsets, parsers
from collection.serializers import CollectionSerlializer

class FileViewset(viewsets.ModelViewSet):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerlializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    http_method_names = ['get', 'post', 'patch', 'delete']