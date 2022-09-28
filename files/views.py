from rest_framework import viewsets, parsers
from .models import File
from collection.models import Collection
from .serializers import FileSerializer
from collection.views import get_token, decode_token
from rest_framework.response import Response
from users.models import User
from .__init__ import *

class FileViewset(viewsets.ModelViewSet):
    queryset = File.objects.all()
    serializer_class = FileSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    http_method_names = ['post', 'patch', 'delete']

    def create(self, request):
        # authenticates user
        token = decode_token(get_token(request))
        if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
            return Response(status=token)

        username = token['username']
        name = request.data.get('colln')

        # collection with that name already exists
        colln = Collection.objects.filter(name=name).first()
        if colln:
            # file title already exists
            if colln.allFiles.filter(title=request.data.get('title')):
                return Response(status=INVALID_DATA_CODE)
        else:
            return Response(status=INVALID_DATA_CODE, data={'message': 'Collection does not exist'})
        
        user = User.objects.filter(username=username).first()

        # request must have an owner (user)
        if user is None:
            return Response(status=INVALID_DATA_CODE)

        
        serializer = FileSerializer(data=request.data)
        if serializer.is_valid():
            colln.num_items += 1
            colln.size = 0
            colln.allFiles.add(serializer.save())
            colln.save()
            return Response(serializer.data, status=OK_STAT_CODE)

        return Response(status=INVALID_DATA_CODE)
