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
        request_status = authenticate_token(request, 'GET')
        if request_status == BAD_REQ_CODE or request_status == INVALID_DATA_CODE:
            return Response(status=request_status)

        username = get_username(request)
        collections = Collection.objects.filter(owner=username)
        serializer = CollectionSerlializer(collections, many=True)
        return Response(serializer.data, status=OK_STAT_CODE)

    def retrieve(self, request, pk):

        # authenticates user
        request_status = authenticate_token(request, 'GET')
        if request_status == BAD_REQ_CODE or request_status == INVALID_DATA_CODE:
            return Response(status=request_status)

        colln = Collection.objects.filter(name=pk).first()
        if not colln:
            return Response(status=NOT_FOUND)
        serializer = CollectionSerlializer(colln)
        return Response(serializer.data, status=OK_STAT_CODE)

    def create(self, request):

        # authenticates user
        request_status = authenticate_token(request, 'POST')
        if request_status == BAD_REQ_CODE or request_status == INVALID_DATA_CODE:
            return Response(status=request_status)

        username = get_username(request)
        name = request.data.get('name')
        colln = Collection.objects.filter(name=name)
        if colln:
            return Response(status=INVALID_DATA_CODE)
        request.data['owner'] = User.objects.filter(username=username).first().username
        request.data['num_items'] = 0
        request.data['size'] = 0
        serializer = CollectionSerlializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=OK_STAT_CODE)


def authenticate_token(request, req_type):
    token = get_token(request, req_type)
    if not token:
        return BAD_REQ_CODE
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
    except Exception:
        return INVALID_DATA_CODE


def get_token(request, req_type):
    if req_type == 'GET':
        return request.GET.get('authToken', None)
    elif req_type == 'POST':
        return request.data.get('authToken', None)


def get_username(request):
    token = request.data.get('authToken')
    return jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')['username']
