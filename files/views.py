from rest_framework import viewsets, parsers
from .models import File
from collection.models import Collection
from .serializers import FileSerializer
from collection.views import get_token, decode_token
from rest_framework.response import Response
from users.models import User
from django.http import QueryDict
from .__init__ import *
from rest_framework import filters

class FileViewset(viewsets.ModelViewSet):
    lookup_value_regex = '[\w.]+' 
    serializer_class = FileSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    http_method_names = ['get', 'post', 'patch', 'delete']
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']

    def list(self, request):
        """
        Parameters:
            request: HttpResponse - contains information of the request, in this case the name of the collection
            which the files are being requested
        Returns:
            Serialized data of all the files in the requested collection (if successful) and well as the status code
        """
        # authenticates user
        token = decode_token(get_token(request))
        
        if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
            return Response(status=token, data={'message': 'Invalid token'})

        username = token['username']

        user = User.objects.filter(username=username).first()
        if user is None:
            return Response(status=INVALID_DATA_CODE, data={'message': 'User does not exist'})
        
        # get files owned by requesting user
        queryset = File.objects.filter(owner=user.username)
        
        # nothing found
        if queryset is None:
            return Response(NOT_FOUND)

        queryset = self.filter_queryset(queryset)

        serializer = FileSerializer(queryset, many=True)
        return Response(serializer.data, status=OK_STAT_CODE)
    
    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    # not being used
    def retrieve(self, request, pk):
        """
        Parameters:
            request: HttpResponse - Contains information such as the file title and the name of the collection it
            belongs to
        Request:
            Returns the serialized data of the file (if successful) and the status code

        """
        # authenticates user
        token = decode_token(get_token(request))
        if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
            return Response(status=token)


        owner = request.data.get('owner')
        if owner is None:
            owner = token['username']
        # check that the user that owns the file exists
        user = User.objects.filter(username=owner).first()
        if user is None:
            return Response(status=INVALID_DATA_CODE, data={'message': 'User does not exist'})

        # check that the collection that file belongs to exists
        collnName = request.data.get('collnName', None)
        colln = Collection.objects.filter(name=collnName, owner=owner)
        if request.data.get('owner') is not None:
            colln = colln.filter(private="false").first()
        else:
            colln = colln.first()

        if colln is None:
            return Response(status=INVALID_DATA_CODE, data={'message': 'Collection does not exist'})

        file = File.objects.filter(title=pk, owner=user, colln=colln.id).first()

        # check that the file requested exists
        if file is None:
            return Response(status=NOT_FOUND)
        
        serializer = FileSerializer(file)
        return Response(serializer.data, status=OK_STAT_CODE)

    def create(self, request):
        """
        Parameters:
            request: HttpResponse - Contains information such as the file title, collection it belongs to and the file
        Returns:
             Returns the serialized file data if successful and the status code
        """

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
        request.data['colln'] = Collection.objects.filter(name=request.data['colln']).first().id
        serializer = FileSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            colln.num_items += 1
            colln.size = 0
            colln.allFiles.add(serializer.save())
            colln.save()
            return Response(serializer.data, status=OK_STAT_CODE)

        return Response(status=INVALID_DATA_CODE, data={'message': 'Invalid data'})
    
    def destroy(self, request, pk):
        """
        Parameters:
            request: HttpResponse - Contains information such as the collection the file belongs
        Returns:
            Returns the status code
        """
        # authenticates user
        token = decode_token(get_token(request))
        if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
            return Response(status=token)
        
        username = token['username']
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response(status=INVALID_DATA_CODE, data={'message': 'User does not exist'})

        colln = Collection.objects.filter(name=request.data.get('collnName', None)).first()
        if colln is None:
            return Response(status=INVALID_DATA_CODE, data={'message': 'Collection does not exist'})

        colln_id = colln.id
        file = File.objects.filter(title=pk, owner=user.username, colln=colln_id).first()

        if file is None:
            return Response(status=INVALID_DATA_CODE)
        
        file.delete()
        return Response(status=OK_STAT_CODE)
