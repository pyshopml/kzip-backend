from django.shortcuts import render
from rest_framework import viewsets
from .serializers import UserSerializer
from .models import ExtUser


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = ExtUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
