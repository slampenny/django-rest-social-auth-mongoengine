import logging
import warnings
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from django.apps import apps as django_apps
from django.conf import settings

from django_mongoengine import fields
from django_mongoengine.mongo_auth.models import User
from rest_framework_mongoengine import serializers


l = logging.getLogger(__name__)


class OAuth2InputSerializer(serializers.DocumentSerializer):

    provider = fields.StringField(null=True, blank=True)
    code = fields.StringField()
    redirect_uri = fields.StringField(null=True, blank=True)


class OAuth1InputSerializer(serializers.DocumentSerializer):

    provider = fields.StringField(null=True, blank=True)
    oauth_token = fields.StringField()
    oauth_token_secret = fields.StringField()
    oauth_verifier = fields.StringField()


class UserSerializer(serializers.DocumentSerializer):

    class Meta:
        model = User
        exclude = ('_id', 'is_staff', 'is_active', 'date_joined', 'password',
                   'last_login', 'user_permissions', 'groups', 'is_superuser',)


class TokenSerializer(serializers.DocumentSerializer):

    token = serializers.SerializerMethodField()

    def get_token(self, obj):
        token, created = Token.objects.get_or_create(user=obj)
        return token.key


class UserTokenSerializer(TokenSerializer, UserSerializer):
    pass


class JWTSerializer(TokenSerializer):

    def get_token(self, obj):
        try:
            from rest_framework_jwt.settings import api_settings
        except ImportError:
            warnings.warn('djangorestframework-jwt must be installed for JWT authentication',
                          ImportWarning)
            raise

        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(self.get_jwt_payload(obj))
        token = jwt_encode_handler(payload)

        return token

    def get_jwt_payload(self, obj):
        """
        Define here, what data shall be encoded in JWT.
        By default, entire object will be encoded.
        """
        return obj


class UserJWTSerializer(JWTSerializer, UserSerializer):
    pass
