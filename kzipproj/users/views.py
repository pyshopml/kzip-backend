from django.contrib.auth.tokens import default_token_generator
from rest_framework import generics
from rest_framework import response
from rest_framework import status
from rest_framework.authentication import BasicAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from .permissions import IsOwnerOrReadOnly
from .serializers import UserSerializer, PasswdResetSerializer, PasswordResetConfirmSerializer, ActivationSerializer
from .models import ExtUser
from .utils.emails import UserPasswordResetEmail, UserActivationEmail, UserConfirmationEmail
from .utils.utils import ActionViewMixin


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


class UserDetail(generics.RetrieveUpdateAPIView):
    """
    View, Update User
    """
    queryset = ExtUser.objects.all()
    serializer_class = UserSerializer
    authentication_classes = (SessionAuthentication, BasicAuthentication)
    permission_classes = (IsOwnerOrReadOnly,)


class PasswordReset(ActionViewMixin, GenericAPIView):
    """
    Reset password
    """

    serializer_class = PasswdResetSerializer
    permission_classes = (AllowAny,)

    def _action(self, serializer):
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


class PasswordResetConfirmView(ActionViewMixin, generics.GenericAPIView):
    """
    Use this endpoint to finish reset password process.
    """
    permission_classes = (AllowAny,)
    token_generator = default_token_generator

    def get_serializer_class(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()

        return PasswordResetConfirmSerializer

    def _action(self, serializer):
        serializer.user.set_password(serializer.data['new_password'])
        serializer.user.save()
        email_factory = UserConfirmationEmail.from_request(self.request, user=serializer.user)
        email = email_factory.create()
        email.send()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class ActivationView(ActionViewMixin, generics.GenericAPIView):
    """
    Use this endpoint to activate user account.
    """
    serializer_class = ActivationSerializer
    permission_classes = (AllowAny,)
    token_generator = default_token_generator

    def _action(self, serializer):
        serializer.user.is_active = True
        serializer.user.save()
        email_factory = UserConfirmationEmail.from_request(self.request, user=serializer.user)
        email = email_factory.create()
        email.send()
        return response.Response(status=status.HTTP_204_NO_CONTENT)
