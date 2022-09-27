import json

from collection.models import Collection
from rest_framework import viewsets, parsers
from collection.serializers import CollectionSerlializer
from rest_framework.response import Response
from users.models import User
import jwt
from .__init__ import *
from django.conf import settings


class CollectionViewSet(viewsets.ViewSet):

    def list(self, request):
        # authenticates user
        token = decode_token(get_token(request, 'GET'))
        if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
            return Response(status=token)
        username = token['username']
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response(status=INVALID_DATA_CODE)
        collections = Collection.objects.filter(owner=user)
        serializer = CollectionSerlializer(collections, many=True)
        return Response(serializer.data, status=OK_STAT_CODE)

    def retrieve(self, request, pk):

        # authenticates user
        token = decode_token(get_token(request, 'GET'))
        if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
            return Response(status=token)
        colln = Collection.objects.filter(name=pk).first()
        if colln is None:
            return Response(status=NOT_FOUND)
        serializer = CollectionSerlializer(colln)
        return Response(serializer.data, status=OK_STAT_CODE)

    def create(self, request):
        # authenticates user
        token = decode_token(get_token(request, 'POST'))
        if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
            return Response(status=token)

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
        req_data_copy = request.data.dict()
        req_data_copy['owner'] = user.username
        req_data_copy['num_items'] = 0
        req_data_copy['size'] = 0
        serializer = CollectionSerlializer(data=req_data_copy)
        serializer.is_valid()

        serializer.save()
        return Response(status=OK_STAT_CODE)

    def destroy(self, request, pk):
        colln = Collection.objects.filter(name=pk)
        if colln is None:
            return Response(status=INVALID_DATA_CODE)
        colln.delete()
        return Response(status=OK_STAT_CODE)

    def update(self, request, pk):
        new_name = request.data.get('name')
        colln = Collection.objects.filter(name=pk)
        if colln is None:
            return Response(status=INVALID_DATA_CODE)
        colln.update(name=new_name)
        return Response(status=OK_STAT_CODE)


def get_token(request, req_type):
    if req_type in ['GET', 'DELETE']:
        return request.GET.get('authToken', None)
    elif req_type in ['POST', 'PUT']:
        return request.data.get('authToken', None)


def decode_token(token):
    if token is None:
        return BAD_REQ_CODE
    try:
        d_token = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
        return d_token
    except Exception:
        return INVALID_DATA_CODE
