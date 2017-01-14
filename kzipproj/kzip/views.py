from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny

from .models import Publication
from .serializers import PublicationSerializer


class PublicationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Publication.objects.all().order_by('-create_date')
    serializer_class = PublicationSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)
    # разрешения: исходя из написанного, авторизованный пользователь может редактировать любую публикацию. Это верно?
    # permission_classes = (AllowAny,)
