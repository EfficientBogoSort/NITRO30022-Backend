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
from rest_framework import filters

class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = CollectionSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    def list(self, request):
        verification, response = verify_user(request)
        if not verification:
            return response
        
        friend_name = request.data.get('friend')

        if friend_name is not None:
            user = User.objects.filter(username=response).first()
            friend = User.objects.filter(username=friend_name).first()
            if friend in user.friends.all():
                queryset = Collection.objects.filter(owner=friend_name, private="false")
            else:
                return Response(status=NOT_FOUND)
        else:
            queryset = Collection.objects.filter(owner=response)

        queryset = self.filter_queryset(queryset)
        # print(queryset)
        serializer = CollectionSerializer(queryset, many=True)
        return Response(serializer.data, status=OK_STAT_CODE)
    
    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def retrieve(self, request, pk):
        verification, response = verify_user(request)
        if not verification:
            return response

        friend_name = request.data.get('friend')

        if friend_name is not None:
            user = User.objects.filter(username=response).first()
            friend = User.objects.filter(username=friend_name).first()
            if friend in user.friends.all():
                colln = Collection.objects.filter(name=pk, owner=friend_name, private="false").first()
            else:
                return Response(status=NOT_FOUND)
        else:
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
        # response is either an error status code if something is wrong
        # or the user's username
        verification, response = verify_user(request)
        if not verification:
            return response
        collnName = request.data.get('name')

        # collection with that name already exists
        colln = Collection.objects.filter(name=collnName, owner_id=response)

        if colln:
            return Response(status=INVALID_DATA_CODE)
        
        request_data_copy = request.data.copy()
        request_data_copy['owner'] = response
        request_data_copy['num_items'] = 0
        request_data_copy['size'] = 0
        request_data_copy['private'] = "true"
        serializer = CollectionSerializer(data=request_data_copy)
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

        new_private = request.data.get('private')
        new_name = request.data.get('name')
        if colln is None:
            return Response(status=NOT_FOUND)

        if new_name is not None:
            colln.name = new_name

        if new_private is not None:
            colln.private = new_private

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
