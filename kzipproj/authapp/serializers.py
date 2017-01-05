from rest_framework import serializers

from .models import ExtUser


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ExtUser
        fields = ('url', 'email', 'name')
