from rest_framework import exceptions
from rest_framework import serializers

from .utils.utils import decode_uid
from .models import ExtUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtUser
        fields = ('email', 'name', 'password')
        extra_kwargs = {'password': {'write_only': True, }}

    def create(self, validated_data):
        user = ExtUser(
            email=validated_data['email'],
            name=validated_data['name'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, user, validated_data):
        user.name = validated_data['name']
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'})

    class Meta:
        model = ExtUser
        fields = ('email', 'name', 'password')
        extra_kwargs = {'password': {'write_only': True},
                        'email': {'read_only': True}
                        }

    def update(self, user, validated_data):
        user.name = validated_data['name']
        user.set_password(validated_data['password'])
        user.save()
        return user


class PasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(style={'input_type': 'password'})
    re_new_password = serializers.CharField(style={'input_type': 'password'})

    default_error_messages = {
        'password_mismatch': 'The two password fields didn\'t match.',
    }

    def validate(self, attrs):
        attrs = super(PasswordSerializer, self).validate(attrs)
        if attrs['new_password'] != attrs['re_new_password']:
            raise serializers.ValidationError(self.error_messages['password_mismatch'])

        return attrs

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class PasswdResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    default_error_messages = {
        'email_not_found': 'User with given email does not exist.'
    }

    def validate_email(self, value):
        if not self.context['view'].get_user(value):
            raise serializers.ValidationError(self.error_messages['email_not_found'])

        return value

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UidAndTokenSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()

    default_error_messages = {
        'invalid_token': 'Invalid token for given user.',
        'invalid_uid': 'Invalid user id or user not exist.',
    }

    def validate_uid(self, value):
        try:
            uid = decode_uid(value)
            self.user = ExtUser.objects.get(pk=uid)
        except (ExtUser.DoesNotExist, ValueError, TypeError, OverflowError) as error:
            raise serializers.ValidationError(self.error_messages['invalid_uid'])
        return value

    def validate(self, attrs):
        attrs = super(UidAndTokenSerializer, self).validate(attrs)
        if not self.context['view'].token_generator.check_token(self.user, attrs['token']):
            raise serializers.ValidationError(self.error_messages['invalid_token'])
        return attrs

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class PasswordResetConfirmSerializer(UidAndTokenSerializer, PasswordSerializer):
    pass


class ActivationSerializer(UidAndTokenSerializer):
    default_error_messages = {
        'stale_token': 'Token invalid',
    }

    def validate(self, attrs):
        attrs = super(ActivationSerializer, self).validate(attrs)
        if self.user.is_active:
            raise exceptions.PermissionDenied(self.error_messages['stale_token'])
        return attrs
