from rest_framework import serializers

from .models import ExtUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtUser
        fields = ('email', 'name', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = ExtUser.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            password=validated_data['password'],
        )
        return user
