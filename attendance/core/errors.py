from django.utils.translation import gettext_lazy as _

EMAIL_WHITELISTED_DOMAIN = "email_whitelisted_domain"

ERRORS_MESSAGE_CODE = {
    EMAIL_WHITELISTED_DOMAIN: {
        "message": _("Email domain is not whitelisted."),
        "status_code": 400,
    },
}
