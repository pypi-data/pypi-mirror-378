
import threading
from django.db import connection
from django_msteams_notify.tasks import send_teams_notification_task
from django_msteams_notify.utils import send_teams_message
from celery import current_app
from django_msteams_notify.models import TeamsNotification
from django_tenants.utils import schema_context

def send_notification_sync_in_thread(instance_id, schema_name):
    """Send Teams notification safely in background thread with proper DB context."""
    with schema_context(schema_name):
        try:
            notification = TeamsNotification.objects.get(id=instance_id)
            send_teams_message(notification)
        except TeamsNotification.DoesNotExist:
            print(f"Notification {instance_id} not found in schema {schema_name}")


def send_notification(instance):
    schema_name = getattr(connection, "schema_name", "public")

    try:
        workers = current_app.control.inspect().ping()
        if workers:
            # Celery is running → async
            send_teams_notification_task.delay(str(instance.id), schema_name)
        else:
            # Celery not running → send in background thread safely
            thread = threading.Thread(
                target=send_notification_sync_in_thread,
                args=(str(instance.id), schema_name)
            )
            thread.start()
    except Exception as exc:
        # fallback to background thread
        print("Celery unavailable, sending in background thread:", exc)
        thread = threading.Thread(
            target=send_notification_sync_in_thread,
            args=(str(instance.id), schema_name)
        )
        thread.start()