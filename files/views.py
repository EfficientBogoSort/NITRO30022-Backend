from rest_framework import viewsets, parsers
from .models import File
from collection.models import Collection
from .serializers import FileSerializer
from collection.views import get_token, decode_token
from rest_framework.response import Response
from users.models import User
from django.http import QueryDict
from .__init__ import *

class FileViewset(viewsets.ModelViewSet):
    # queryset = File.objects.all()
    serializer_class = FileSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def list(self, request):
        # authenticates user
        token = decode_token(get_token(request))
        
        if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
            return Response(status=token, data={'message': 'Invalid token'})
        username = token['username']
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response(status=INVALID_DATA_CODE, data={'message': 'User does not exist'})
        
        queryset = File.objects.filter(owner=user)
        # print(queryset)
        serializer = FileSerializer(queryset, many=True)
        return Response(serializer.data, status=OK_STAT_CODE)

    def retrieve(self, request, pk):
        # authenticates user
        token = decode_token(get_token(request))
        if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
            return Response(status=token)
        # print(token)
        username = token['username']
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response(status=INVALID_DATA_CODE, data={'message': 'User does not exist'})
        
        file = File.objects.filter(id=pk, owner=user.username).first()
        # print("file", file)
        if file is None:
            return Response(status=NOT_FOUND)
        
        serializer = FileSerializer(file)
        return Response(serializer.data, status=OK_STAT_CODE)

    def create(self, request):
        # authenticates user
        token = decode_token(get_token(request))
        if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
            return Response(status=token, data={'message': 'Invalid token'})

        username = token['username']
        name = request.data.get('colln')

        if name is None:
            return Response(status=INVALID_DATA_CODE, data={'message': 'Collection name not provided'})

        # collection with that name already exists
        colln = Collection.objects.filter(name=name).first()
        if colln:
            # file title already exists
            if colln.allFiles.filter(title=request.data.get('title')):
                return Response(status=INVALID_DATA_CODE, data={'message': 'File with that title already exists'})
        else:
            return Response(status=INVALID_DATA_CODE, data={'message': 'Collection does not exist'})
        
        user = User.objects.filter(username=username).first()

        # request must have an owner (user)
        if user is None:
            return Response(status=INVALID_DATA_CODE, data={'message': 'User does not exist'})

        if isinstance(request.data, QueryDict):
            request.data._mutable = True
        request.data['owner'] = user.username
        
        serializer = FileSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            colln.num_items += 1
            colln.size = 0
            colln.allFiles.add(serializer.save())
            colln.save()
            return Response(serializer.data, status=OK_STAT_CODE)

        return Response(status=INVALID_DATA_CODE, data={'message': 'Invalid data'})
    
    def destroy(self, request, pk):
        # authenticates user
        token = decode_token(get_token(request))
        if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
            return Response(status=token)
        
        username = token['username']
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response(status=INVALID_DATA_CODE, data={'message': 'User does not exist'})
        
        file = File.objects.filter(id=pk, owner=user.username).first()

        if file is None:
            return Response(status=INVALID_DATA_CODE)
        
        file.delete()
        return Response(status=OK_STAT_CODE)

    def update(self, request, pk):
        # authenticates user
        token = decode_token(get_token(request))
        if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
            return Response(status=token)
        # print(token)
        username = token['username']
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response(status=INVALID_DATA_CODE, data={'message': 'User does not exist'})
        
        file = File.objects.filter(id=pk, owner=user.username).first()

        new_title = request.data.get('title')
        if file is None:
            return Response(status=INVALID_DATA_CODE)
        file.update(name=new_title)
        return Response(status=OK_STAT_CODE)
