from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'uuid',
            'username',
            'first_name',
            'last_name',
            'first_name_en',
            'last_name_en',
            'email',
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'first_name_en',
            'last_name_en',
        ]


class UserSafeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'uuid',
            'first_name',
            'last_name',
        ]
