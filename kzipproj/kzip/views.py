from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from .permissions import IsOwnerOrReadOnly
from .models import Publication
from .serializers import PublicationSerializer


class PublicationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Publication.objects.all().order_by('-create_date')
    serializer_class = PublicationSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsOwnerOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
