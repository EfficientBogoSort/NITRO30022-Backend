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
        
        # get collections owned by requesting user
        queryset = Collection.objects.filter(owner=response)

        # if requesting user also wants all publicly available collections add to queryset
        public = request.data.get('public')
        if public is not None and public == "true":
            queryset = queryset | Collection.objects.filter(private="false").exclude(owner=response)
        
        # no collections found
        if queryset is None:
            return Response(status=NOT_FOUND)

        queryset = self.filter_queryset(queryset)
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

        owner = request.data.get('owner')

        # if requesting user wants public collection from different user
        if owner is not None:
            colln = Collection.objects.filter(name=pk, owner=owner, private="false").first()
        # else search for collection in requesting user's collections
        else:
            colln = Collection.objects.filter(name=pk, owner=response).first()
        
        # collection doesnt exist
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

        colln = Collection.objects.filter(name=collnName, owner_id=response)

        # collection with that name already exists
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
            return Response(status=NOT_FOUND,data={'message': 'Collection does not exist'})

        colln.delete()

        return Response(status=OK_STAT_CODE)

    def update(self, request, pk, **kwargs):

        verification, response = verify_user(request)
        if not verification:
            return response

        colln = Collection.objects.filter(name=pk, owner=response).first()

        # collection does not exist
        if colln is None:
            return Response(status=NOT_FOUND)

        new_private = request.data.get('private')
        new_name = request.data.get('name')

        # name to be updated
        if new_name is not None and new_name is not "" and new_name is not pk:

            # collection with new name already exists
            dupColln = Collection.objects.filter(name=new_name, owner_id=response).first()
            if dupColln:
                return Response(status=INVALID_DATA_CODE)
            
            colln.name = new_name

        # visibility to be updated
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
