# django_msteams_notify/notification.py
from django.db import connection
from django_msteams_notify.tasks import send_teams_notification_task
from django_msteams_notify.utils import send_teams_message
from django.conf import settings

USE_CELERY = getattr(settings, "USE_CELERY", True)

def send_notification(instance):
    """Send Teams notification either async (Celery) or sync (immediately)."""
    schema_name = getattr(connection, "schema_name", "public")
    if USE_CELERY:
        # Async via Celery
        send_teams_notification_task.delay(str(instance.id), schema_name)
    else:
        # Sync: send immediately
        send_teams_message(instance)
