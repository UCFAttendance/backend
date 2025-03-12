import re

from rest_framework.views import exception_handler
from rest_framework.response import Response

from .errors import ERRORS_MESSAGE_CODE


def core_exception_handler(exc, context):

    handlers = {
        "IntegrityError": _handle_integrity_error,
    }

    exception_class = exc.__class__.__name__

    if exception_class in handlers:
        return handlers[exception_class](exc, context)

    response = exception_handler(exc, context)
    return response


def _handle_integrity_error(exc, context):
    regex = r'violates check constraint "(?P<constraint_name>\w+)"'
    constraint_error = re.search(regex, str(exc)).group("constraint_name")
    if constraint_error in ERRORS_MESSAGE_CODE:
        return Response(
            {"errors": [ERRORS_MESSAGE_CODE[constraint_error]["message"]]},
            status=ERRORS_MESSAGE_CODE[constraint_error]["status_code"],
        )
