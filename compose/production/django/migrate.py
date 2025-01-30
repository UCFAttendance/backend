from django.core.management import call_command


def handler(event, context):
    call_command("migrate")
    return "Migration completed"
