from .models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'username', 'password']
        # do not include the password during the serialization
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class LogInSerializer(serializers.ModelSerializer):

    password = serializers.CharField(max_length=50, min_length=5, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'token']
        read_only_fields = ['token']