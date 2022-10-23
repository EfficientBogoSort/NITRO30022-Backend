from rest_framework import serializers
from users.models import User

class FriendSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['friends']