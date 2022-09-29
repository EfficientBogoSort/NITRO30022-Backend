import json

from collection.models import Collection
from rest_framework import viewsets, parsers
from collection.serializers import CollectionSerializer
from rest_framework.response import Response
from users.models import User
import jwt
from .__init__ import *
from django.conf import settings


class CollectionViewSet(viewsets.ModelViewSet):
    serializer_class = CollectionSerializer
    search_fields = ['name']
    
    def list(self, request):
        # authenticates user
        token = decode_token(get_token(request))
        
        if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
            return Response(status=token, data={'message': 'Invalid token'})
        username = token['username']
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response(status=INVALID_DATA_CODE, data={'message': 'User does not exist'})
        queryset = Collection.objects.filter(owner=user)
        # print(queryset)
        serializer = CollectionSerializer(queryset, many=True)
        return Response(serializer.data, status=OK_STAT_CODE)

    def retrieve(self, request, pk):
        # authenticates user
        token = decode_token(get_token(request))
        if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
            return Response(status=token)
        
        username = token['username']
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response(status=INVALID_DATA_CODE, data={'message': 'User does not exist'})

        colln = Collection.objects.filter(name=pk, owner=user.username).first()
        
        if colln is None:
            return Response(status=NOT_FOUND)
        serializer = CollectionSerializer(colln)
        return Response(serializer.data, status=OK_STAT_CODE)

    def create(self, request):
        # authenticates user
        token = decode_token(get_token(request))
        if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
            return Response(status=token, data={'message': 'Invalid token'})

        username = token['username']
        name = request.data.get('name')

        # collection with that name already exists
        colln = Collection.objects.filter(name=name)
        if colln:
            return Response(status=INVALID_DATA_CODE)
        user = User.objects.filter(username=username).first()

        # request must have an owner (user)
        if user is None:
            return Response(status=INVALID_DATA_CODE)
        
        # request.data._mutable = True
        request.data['owner'] = user.username
        request.data['num_items'] = 0
        request.data['size'] = 0
        print(request.data)
        serializer = CollectionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=OK_STAT_CODE)
        return Response(status=INVALID_DATA_CODE, data={'message': 'Invalid data'})

    def destroy(self, request, pk):
        # authenticates user
        token = decode_token(get_token(request))
        if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
            return Response(status=token)
        # print(token)
        username = token['username']
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response(status=INVALID_DATA_CODE, data={'message': 'User does not exist'})

        colln = Collection.objects.filter(name=pk, owner=user.username).first()
        
        if colln is None:
            return Response(status=INVALID_DATA_CODE)
        colln.delete()
        return Response(status=OK_STAT_CODE)

    def update(self, request, pk, **kwargs):
        # authenticates user
        token = decode_token(get_token(request))
        if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
            return Response(status=token)
        # print(token)
        username = token['username']
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response(status=INVALID_DATA_CODE, data={'message': 'User does not exist'})

        colln = Collection.objects.filter(name=pk, owner=user.username).first()

        new_name = request.data.get('name')
        
        if colln is None:
            return Response(status=INVALID_DATA_CODE)
        colln.update(name=new_name)
        return Response(status=OK_STAT_CODE)


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
