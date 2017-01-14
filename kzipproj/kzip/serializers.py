from rest_framework import serializers
from .models import Publication


class PublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publication
        # fields = ('id', 'title', 'text', 'create_date')
        fields = ('id', 'user', 'title', 'text', 'create_date')
