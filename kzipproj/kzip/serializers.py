from rest_framework import serializers
from kzip.models import Publication


class PublicationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Publication
        fields = ('user', 'title', 'text', 'create_date')
