from rest_framework import response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import GenericAPIView, CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny

from .permissions import IsOwnerOrReadOnly
from .serializers import *
from .models import ExtUser
from .utils.emails import UserPasswordResetEmail, UserActivationEmail, UserConfirmationEmail


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
        email_factory = UserConfirmationEmail.from_request(self.request, user=serializer.user)
        email = email_factory.create()
        email.send()
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
        email_factory = UserConfirmationEmail.from_request(self.request, user=serializer.user)
        email = email_factory.create()
        email.send()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
