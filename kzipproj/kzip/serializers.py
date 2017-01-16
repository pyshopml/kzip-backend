from rest_framework import serializers
from .models import Publication


class PublicationSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.get_full_name')

    class Meta:
        model = Publication
        fields = ('id', 'user', 'title', 'text', 'create_date')
