import json

from collection.models import Collection
from rest_framework import viewsets, parsers
from rest_framework.decorators import action
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
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    search_fields = ['name']

    def list(self, request):
        """
        Parameters:
            request: HttpRequest - Contains the request information such as visibility of the collection
        Returns:
            response: Response - Returns a list of all the collections belonging to the user if successful and the
                status code
        """
        verification, response = verify_user(request)
        if not verification:
            return response

        # get collections owned by requesting user
        queryset = Collection.objects.filter(owner=response)

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
        """
        Parameters:
          request: HttpRequest - Contains the request information such as the collection name, the owner of the
            collection
        Returns:
          response: Response - Returns the serialized data of the requested collection if successful  and
          the status code
        """
        verification, response = verify_user(request)
        if not verification:
            return response

        # search for collection owned by requesting user
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
        """
        Parameters:
          request: HttpRequest - Contains the request information such as the collection name
        Returns:
          response: Response - Returns the serialized collection data if successful and the status code
        """

        # response is either an error status code if something is wrong
        # or the user's username
        verification, response = verify_user(request)
        if not verification:
            return response
        colln_name = request.data.get('name')

        colln = Collection.objects.filter(name=colln_name, owner_id=response)

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
        """
        Parameters:
          request: HttpRequest - Not used except for verification purposes as the name is contained in the url
        Returns:
          response: Response - Returns the status code
        """
        verification, response = verify_user(request)
        if not verification:
            return response

        colln = Collection.objects.filter(name=pk, owner=response).first()

        if colln is None:
            return Response(status=NOT_FOUND, data={'message': 'Collection does not exist'})

        colln.delete()

        return Response(status=OK_STAT_CODE)

    def update(self, request, pk, **kwargs):
        """
        Parameters:
          request: HttpRequest - Contains the request information such as the collection name and the
            visibility (if changed)
        Returns:
          response: Response - Returns the status code
        """
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
        if new_name is not None and new_name != "" and new_name != colln.name:

            # collection with new name already exists
            dup_colln = Collection.objects.filter(name=new_name, owner_id=response).first()
            if dup_colln:
                return Response(status=INVALID_DATA_CODE)

            colln.name = new_name

        # visibility to be updated
        if new_private is not None:
            colln.private = "true" if (new_private == True or new_private == "true") else "false"

        colln.save()

        return Response(status=OK_STAT_CODE)

    @action(detail=False, name='search')
    def search(self, request):
        """
        Parameters:
          request: HttpRequest - Contains the request information in the headers (no payload)
        Returns:
          response: Response - Returns the serialized collections data if successful and the status code
        """

        verification, response = verify_user(request)
        if not verification:
            return response

        # get collections owned by requesting user and all public collections
        queryset = Collection.objects.filter(owner=response) | Collection.objects.filter(private="false").exclude(owner=response)

        # no collections found
        if queryset is None:
            return Response(status=NOT_FOUND)

        queryset = self.filter_queryset(queryset)
        serializer = CollectionSerializer(queryset, many=True)

        return Response(serializer.data, status=OK_STAT_CODE)

    @action(detail=True, methods=['post'], name='public')
    def public(self, request, pk=None):
        """
        Parameters:
          request: HttpRequest - Contains the request information in the headers (no payload)
        Returns:
          response: Response - Returns the serialized collection data if successful and the status code
        """

        verification, response = verify_user(request)
        if not verification:
            return response

        owner = request.data.get('owner')

        # search for collection owned by requesting user
        colln = Collection.objects.filter(name=pk, owner=owner).first()

        # collection doesnt exist
        if colln is None:
            return Response(status=NOT_FOUND)

        serializer = CollectionSerializer(colln)
        files_data = File.objects.filter(id__in=serializer.data['allFiles'])
        serialized_file_data = FileSerializer(files_data, many=True)
        full_data = {'files_data': serialized_file_data.data}
        full_data.update(serializer.data)

        return Response(full_data, status=OK_STAT_CODE) 
        

def verify_user(request):
    """
    Parameters:
        request: HttpRequest - Contains the header containing the JWT token for authentication purposes
    Returns:
        if successful:
            (verified, username): (Boolean, String) - Returns a 2 tuple where the second field is the username
        else:
            (verified, response): (Boolean, Response) - Returns a 2 tuple where the second field is a Response object
                that contains the appropriate status code
    """
    token = decode_token(get_token(request))
    if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
        return False, Response(status=token)
    username = token['username']
    user = User.objects.filter(username=username).first()
    if user is None:
        return False, Response(status=NOT_FOUND, data={'message': 'User does not exist'})
    return True, username


def get_token(request):
    """
    Parameters:
        request: HttpRequest - Contains the header with the JWT token
    Returns:
        token: String - returns the token in a string form otherwise None if it's absent
    """
    if request.META.get('HTTP_AUTHORIZATION'):
        token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]
        return token
    return None


def decode_token(token):
    """
    Parameters:
        token: string - JWT token as a string for authentication
    Returns:
        if successful:
            d_token: Dictionary - The decoded token with information such as the username and expiration time
    """
    if token is None:
        return BAD_REQ_CODE
    try:
        d_token = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
        return d_token
    except Exception:
        return INVALID_DATA_CODE
