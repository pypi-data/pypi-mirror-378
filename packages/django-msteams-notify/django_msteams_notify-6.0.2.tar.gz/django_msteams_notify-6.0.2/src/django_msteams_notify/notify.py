from django.db import connection
from django_msteams_notify.tasks import send_teams_notification_task
from django_msteams_notify.utils import send_teams_message
from celery import current_app

def send_notification(instance):
    """Send Teams notification via Celery if possible, else sync."""
    schema_name = getattr(connection, "schema_name", "public")

    # Check if Celery broker is available
    if current_app.control.inspect().ping() is not None:
        # Celery is running → async
        send_teams_notification_task.delay(str(instance.id), schema_name)
    else:
        # Celery not running → send immediately
        send_teams_message(instance)
