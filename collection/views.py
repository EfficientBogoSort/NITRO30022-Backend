import json

from collection.models import Collection
from rest_framework import viewsets
from collection.serializers import CollectionSerializer
from rest_framework.response import Response
from users.models import User
import jwt
from .__init__ import *
from django.conf import settings
from files.models import File
from files.serializers import FileSerializer

class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = CollectionSerializer
    search_fields = ['name']
    
    def list(self, request):
        verification, response = verify_user(request)
        if not verification:
            return response
        queryset = Collection.objects.filter(owner=response)
        # print(queryset)
        serializer = CollectionSerializer(queryset, many=True)
        return Response(serializer.data, status=OK_STAT_CODE)

    def retrieve(self, request, pk):
        verification, response = verify_user(request)
        if not verification:
            return response

        colln = Collection.objects.filter(name=pk, owner=response).first()
        
        if colln is None:
            return Response(status=NOT_FOUND)
        serializer = CollectionSerializer(colln)
        files_data = File.objects.filter(id__in=serializer.data['allFiles'])
        serialized_file_data = FileSerializer(files_data, many=True)
        full_data = {'files_data': serialized_file_data.data}
        full_data.update(serializer.data)
        return Response(full_data, status=OK_STAT_CODE)

    def create(self, request):
        verification, response = verify_user(request)
        if not verification:
            return response
        name = request.data.get('name')

        # collection with that name already exists
        colln = Collection.objects.filter(name=name)
        if colln:
            return Response(status=INVALID_DATA_CODE)
        
        request.data._mutable = True
        request.data['owner'] = response
        request.data['num_items'] = 0
        request.data['size'] = 0
        serializer = CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=OK_STAT_CODE)
    def destroy(self, request, pk):
        verification, response = verify_user(request)
        if not verification:
            return response

        colln = Collection.objects.filter(name=pk, owner=response).first()
        
        if colln is None:
            return Response(status=NOT_FOUND)
        colln.delete()
        return Response(status=OK_STAT_CODE)

    def update(self, request, pk, **kwargs):
        verification, response = verify_user(request)
        if not verification:
            return response

        colln = Collection.objects.filter(name=pk, owner=response).first()

        new_name = request.data.get('name')
        if colln is None:
            return Response(status=NOT_FOUND)
        colln.name = new_name
        colln.save()
        return Response(status=OK_STAT_CODE)

def verify_user(request):
    token = decode_token(get_token(request))
    if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
        return False, Response(status=token)
    username = token['username']
    user = User.objects.filter(username=username).first()
    if user is None:
        return False, Response(status=NOT_FOUND, data={'message': 'User does not exist'})
    return True, username

def get_token(request):
    if request.META.get('HTTP_AUTHORIZATION'):
        token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
        return token
    return None


def decode_token(token):
    if token is None:
        return BAD_REQ_CODE
    try:
        d_token = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
        return d_token
    except Exception:
        return INVALID_DATA_CODE
