from django.conf import settings
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from rest_framework import generics, permissions

from .serializers import UserSerializer

User = get_user_model()


class UserDetail(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class LoginRedirect(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def redirect(self, request, *args, **kwargs):
        return redirect(settings.FRONTEND_BASE_URL)

    def get(self, request, *args, **kwargs):
        return self.redirect(request, *args, **kwargs)


class PasswordResetConfirmRedirectView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def redirect(self, request, *args, **kwargs):
        return redirect(
            f"{settings.FRONTEND_BASE_URL}/auth/password-reset-confirm/?uid={kwargs['uid']}&token={kwargs['token']}&role={kwargs['role']}"
        )

    def get(self, request, *args, **kwargs):
        return self.redirect(request, *args, **kwargs)
