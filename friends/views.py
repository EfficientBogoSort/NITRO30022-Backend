from users.models import User
from rest_framework import viewsets
from rest_framework.response import Response
from collection.views import get_token, decode_token
from users.__init__ import *
from friends.serializers import FriendSerializer


"""
Unfinished feature: It is not being currently used as it is not finished
"""
class FriendViewSet(viewsets.ModelViewSet):

    def create(self, request):
        token = decode_token(get_token(request))
        if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
            return Response(status=token)
        username = token.get('username', None)
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response(status=NOT_FOUND, data={'message': 'User not found'})
        friendUsername = request.data.get('friendUsername', None)
        friend = User.objects.filter(username=friendUsername).first()
        if friend is None:
            return Response(status=NOT_FOUND, data={'message': 'Friend not found'})
        user.friends.add(friend)
        return Response(status=OK_STAT_CODE)

    def destroy(self, request, pk):
        token = decode_token(get_token(request))
        if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
            return Response(status=token)

        username = token['username']
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response(status=NOT_FOUND, data={'message': 'User does not exist'})
        friend = User.objects.filter(username=pk).first()
        if friend is None:
            return Response(status=NOT_FOUND, data={'message': 'Friend not found'})
        user.friends.remove(friend)
        return Response(status=OK_STAT_CODE)

    def list(self, request):
        token = decode_token(get_token(request))
        if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
            return Response(status=token)
        username = token.get('username', None)
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response(status=NOT_FOUND, data={'message': 'User not found'})
        serialized_friends = FriendSerializer(user)
        return Response(serialized_friends.data, status=OK_STAT_CODE)

    # don't see a need for this except to retrive profile picture in the future
    def retrieve(self, request, pk):
        token = decode_token(get_token(request))
        if token == INVALID_DATA_CODE or token == BAD_REQ_CODE:
            return Response(status=token)
        username = token.get('username', None)
        user = User.objects.filter(username=username).first()
        if user is None:
            return Response(status=NOT_FOUND, data={'message': 'User not found'})
        friend = User.objects.filter(username=pk).first()
        if friend is None:
            return Response(status=NOT_FOUND, data={'message': 'Friend not found'})

