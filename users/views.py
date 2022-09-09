"""
views.py description here
"""

from rest_framework.response import Response
from .serializers import UserSerializer, LogInSerializer
from rest_framework.views import APIView
from .models import User
from rest_framework.decorators import api_view
import jwt
from django.conf import settings
from datetime import datetime
# Create your views here.

TOKEN_DURATION = 5


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
        # create a new user and add it to the db
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # create a token for the new user
        username = serializer.data['username']
        user = User.objects.filter(username=username).first()
        user_serializer = LogInSerializer(user)

        return Response(user_serializer.data, status=200)


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
            return Response(status=401)
        # the serializer craetes a JWT token for the user to use
        user_serialized_data = LogInSerializer(user)
        return Response(user_serialized_data.data, status=200)

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
    # returns 404 for when the token is not in the request, the username is not in the token, the token expired
    # or the user is not in the database
    if not token:
        return Response(status=404)
    decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
    if 'username' not in decoded_token or decoded_token['exp'] > datetime.utcnow():
        return Response(404)
    user = User.objects.filter(username=decoded_token['username']).first()
    if user is None:
        return Response(status=404)
    user_serialized_data = UserSerializer(user)
    return Response(user_serialized_data.data, status=200)