from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

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
    #
    # разрешение AllowAny использовалось во время разработки приложения kzip без использования приложения users(как заглушка),
    # строчку удалил.
