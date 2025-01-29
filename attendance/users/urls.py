from django.urls import include, path

from .views import LoginRedirect, UserDetail

app_name = "users"
urlpatterns = [
    path("", include("dj_rest_auth.urls")),
    path("registration/", include("dj_rest_auth.registration.urls")),
    path("me/", UserDetail.as_view(), name="user_detail"),
    path("redirect/", LoginRedirect.as_view(), name="auth_redirect"),
]
