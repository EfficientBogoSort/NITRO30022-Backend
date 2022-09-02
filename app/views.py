from rest_framework.response import Response
from rest_framework.decorators import api_view
from .models import File, Collection
from .serializers import FileSerializer, CollectionSerializer

from rest_framework.parsers import JSONParser

@api_view(['GET', 'POST'])
def files(request, format=None):
    """
    PARAMS:
    request: request object
    RETURN: response object
    DESCRIPTION: This function is used to get all files or create a new file.
    """
    if request.method == 'GET':
        files = File.objects.all()
        serializer = FileSerializer(files, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = FileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)


@api_view(['GET', 'POST'])
def collections(request, format=None):
    if request.method == 'GET':
        collections = Collection.objects.all()
        serializer = FileSerializer(collections, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = FileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)

@api_view(['GET', 'PUT', 'DELETE'])
def collection(request, id, format=None):
    try:
        collection = Collection.objects.get(pk=id)
    except Collection.DoesNotExist:
        return Response(status=404)
    
    if request.method == 'GET':
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = CollectionSerializer(collection, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)
    elif request.method == 'DELETE':
        collection.delete()
        return Response(status=204)
