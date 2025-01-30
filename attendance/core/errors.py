from django.utils.translation import gettext_lazy as _

EMAIL_WHITELISTED_DOMAIN = "email_whitelisted_domain"
USER_UNIQUE_EMAIL = "users_user_email_key"

ERRORS_MESSAGE_CODE = {
    EMAIL_WHITELISTED_DOMAIN: {
        "message": _("Email domain is not whitelisted."),
        "status_code": 400,
    },
    USER_UNIQUE_EMAIL: {
        "message": _("User with this email already exists."),
        "status_code": 400,
    },
}
