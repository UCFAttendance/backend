from django.urls import include, path

from .views import LoginRedirect, PasswordResetConfirmRedirectView, UserDetail

urlpatterns = [
    path("", include("dj_rest_auth.urls")),
    path(
        "password-reset/<str:uid>/<str:token>/",
        PasswordResetConfirmRedirectView.as_view(),
        name="password_reset_confirm",
    ),
    path("registration/", include("dj_rest_auth.registration.urls")),
    path("me/", UserDetail.as_view(), name="user_detail"),
    path("redirect/", LoginRedirect.as_view(), name="auth_redirect"),
]
