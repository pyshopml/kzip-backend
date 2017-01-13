from rest_framework import response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import GenericAPIView, CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from django.contrib.auth import authenticate, login, logout
from .signals import senders
from .permissions import IsOwnerOrReadOnly
from .serializers import *
from .models import ExtUser
from .utils.emails import UserPasswordResetEmail, UserActivationEmail, UserConfirmationEmail
from .signals.receivers import send_success_mail


class UserCreate(CreateAPIView):
    """
    Create a User
    """
    serializer_class = UserSerializer
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save()
        self.send_activation_email(user)

    def send_activation_email(self, user):
        email_factory = UserActivationEmail.from_request(self.request, user=user)
        email = email_factory.create()
        email.send()


class UserDetail(RetrieveUpdateAPIView):
    """
    View, Update User
    """
    queryset = ExtUser.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsOwnerOrReadOnly,)


class PasswordReset(GenericAPIView):
    """
    Reset password
    """

    serializer_class = PasswdResetSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.get_user(serializer.data['email'])
        self.send_password_reset_email(user)
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    def get_user(self, email):
        user = ExtUser.objects.get(email=email)
        return user

    def send_password_reset_email(self, user):
        email_factory = UserPasswordResetEmail.from_request(self.request, user=user)
        email = email_factory.create()
        email.send()


class PasswordResetConfirmView(GenericAPIView):
    """
    Use this endpoint to finish reset password process.
    """
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = (AllowAny,)
    token_generator = default_token_generator

    def get(self, request, *args, **kwargs):
        serializer = UidAndTokenSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        return response.Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.user.set_password(serializer.data['new_password'])
        serializer.user.save()
        senders.confim_email.send(
            sender=self.__class__, user=serializer.user, request=self.request)
        return response.Response(status=status.HTTP_202_ACCEPTED)


class ActivationView(GenericAPIView):
    """
    Use this endpoint to activate user account.
    """
    serializer_class = ActivationSerializer
    permission_classes = (AllowAny,)
    token_generator = default_token_generator

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.GET)
        serializer.is_valid(raise_exception=True)
        return self._action(serializer)

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._action(serializer)

    def _action(self, serializer):
        serializer.user.is_active = True
        serializer.user.save()
        senders.confim_email.send(
            sender=self.__class__, user=serializer.user, request=self.request)
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class Login(GenericAPIView):
    """
    Use this endpoint to login user .
    """
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def get(self, request):
        serializer = self.serializer_class()
        return response.Response(serializer.data, status=status.HTTP_204_NO_CONTENT)

    def post(self, request):
        data = request.POST
        email = data.get('email', None)
        password = data.get('password', None)

        user = authenticate(email=email, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                serializer = self.serializer_class(user)
                return response.Response(serializer.data)
            else:
                return response.Response({
                    'status': 'Unauthorized',
                    'message': 'This account has been disabled.'
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return response.Response({
                'status': 'Unauthorized',
                'message': 'Invalid credentials.'
            }, status=status.HTTP_401_UNAUTHORIZED)


class Logout(APIView):
    """
    Use this endpoint to logout user .
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        logout(request)
        return response.Response({
            'status': 'Logout Success',
        },
            status=status.HTTP_200_OK)

    def post(self, request):
            logout(request)
            return response.Response({
                'status': 'Logout Success',
            },
                status=status.HTTP_200_OK)
