from rest_framework import generics
from rest_framework import mixins
from rest_framework import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated

from .permissions import IsOwnerOrReadOnly
from .serializers import UserSerializer
from .models import ExtUser


class UserCreate(generics.CreateAPIView):
    """
    Create a User
    """
    serializer_class = UserSerializer
    authentication_classes = ()
    permission_classes = (AllowAny,)


class UserDetail(generics.RetrieveUpdateAPIView):
    """
    View Update User
    """
    queryset = ExtUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsOwnerOrReadOnly,)
