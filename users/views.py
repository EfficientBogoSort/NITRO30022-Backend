from rest_framework.response import Response
from .serializers import UserSerializer, LogInSerializer
from rest_framework.views import APIView
from .models import User
from rest_framework.decorators import api_view
import jwt
from django.conf import settings
from datetime import datetime
from .__init__ import *
from collection.views import verify_user


class RegisterView(APIView):
    """
    Contains request methods for the register view
    """

    def post(self, request):
        """
        Parameters:
            request: HttpRequest - contains signup data such as name, last name, username, password and email to create
            a new user in the database
        Return: returns a fresh JWT token for the user as well as the status code
        """
        username = request.data.get('username', None)
        user = User.objects.filter(username=username).first()
        if user:
            return Response(status=INVALID_DATA_CODE)
        # create a new user and add it to the db
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # create a token for the new user
        username = serializer.data['username']
        user = User.objects.filter(username=username).first()
        user_serializer = LogInSerializer(user)

        return Response(user_serializer.data, status=OK_STAT_CODE)


class LogInView(APIView):
    """
    Contains request methods for the log in view
    """

    def post(self, request):
        """
        Parameters:
            request: HttpRequest - contains the username and password that the user inputted
        Return: 
            if the user successfully authenticated, it will return the login serialized data, which includes 
            username and a new JWT token. If the user failed to authenticate, it will return a status code 401
        """
        username = request.data.get('username', None)
        password = request.data.get('password', None)

        # verify user exists
        user = User.objects.filter(username=username).first()
        if user is None or not user.check_password(password):
            return Response(status=INVALID_DATA_CODE)
        # the serializer creates a JWT token for the user to use
        user_serialized_data = LogInSerializer(user)
        return Response(user_serialized_data.data, status=OK_STAT_CODE)


@api_view(['POST'])
def get_user(request):
    """
    Parameters:
        request: HttpRequest - contains the token used to retrieve the user from the database
    Return:
        Response: contains data in response to the request (such as user information, or JWT token)as well as
        the status code
    """
    token = request.data.get('authToken')
    if not token:
        return Response(status=BAD_REQ_CODE)

    # check if the token is still valid (within its lifetime)
    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
    except jwt.exceptions.ExpiredSignatureError:
        return Response(status=INVALID_DATA_CODE)

    user = User.objects.filter(username=decoded_token['username']).first()
    if user is None:
        return Response(status=NOT_FOUND)
    user_serialized_data = UserSerializer(user)
    return Response(user_serialized_data.data, status=OK_STAT_CODE)

@api_view(['PUT'])
def update_user_info(request):
    """
    Parameters:
        request: HttpRequest - contains the token used to retrieve the user from the database
     Return:
        Response: contains data in response to the request as well as the request data
    """
    verification, response = verify_user(request)
    if not verification:
        return response
    username = response

    user = User.objects.filter(username=username).first()
    if user is None:
        return Response(status=NOT_FOUND)

    new_email = request.data.get('email', None)
    new_password = request.data.get('password', None)

    # update the requested fields
    if new_email is not None:
        user.email = new_email
    
    if new_password is not None:
        user.set_password(new_password)
    
    if new_email is None and new_password is None:
        return Response(status=INVALID_DATA_CODE)
    
    user.save()
    return Response(request.data, status=OK_STAT_CODE)

    