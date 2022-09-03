from rest_framework.response import Response
from .serializers import UserSerializer, LogInSerializer
from rest_framework.views import APIView
from .models import User

# Create your views here.

TOKEN_DURATION = 5


class RegisterView(APIView):
    def post(self, request):
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

    def post(self, request):
        username = request.data.get('username', None)
        password = request.data.get('password', None)

        # find a user with a matching username and check if the password is correct
        user = User.objects.filter(username=username).first()
        if user is None or not user.check_password(password):
            return Response(status=401)
        # the user authenticated, generate a JWT token for the user, which is done by the serializer
        serializer = LogInSerializer(user)
        return Response(serializer.data, status=200)