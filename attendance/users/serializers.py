from allauth.account.utils import user_pk_to_url_str
from allauth.utils import build_absolute_uri
from dj_rest_auth.serializers import PasswordResetSerializer
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import serializers

from attendance.users.models import User as UserType

User = get_user_model()


class UserSerializer(serializers.ModelSerializer[UserType]):
    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "email",
            "role",
        ]


class CustomPasswordResetSerializer(PasswordResetSerializer):
    @staticmethod
    def custom_url_generator(request, user, temp_key):
        path = reverse(
            "password_reset_confirm",
            args=[user_pk_to_url_str(user), user.role, temp_key],
        )
        url = build_absolute_uri(request, path)
        url = url.replace("%3F", "?")
        return url

    def get_email_options(self):
        return {
            "url_generator": CustomPasswordResetSerializer.custom_url_generator,
        }
