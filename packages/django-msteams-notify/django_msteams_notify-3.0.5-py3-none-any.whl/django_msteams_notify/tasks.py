from celery import shared_task
from django_msteams_notify.models import TeamsNotification
from django_msteams_notify.utils import send_teams_message
from django.conf import settings
from uuid import UUID

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def send_teams_notification_task(self, notification_id):
    """
    Send a Teams notification asynchronously with retries.
    Handles UUIDs and updates notification status.
    """
    try:
        notification = TeamsNotification.objects.get(id=UUID(notification_id))
    except (TeamsNotification.DoesNotExist, ValueError):
        return False

    # Ensure webhook URL is available
    if not getattr(settings, "TEAMS_WEBHOOK_URL", None):
        notification.status = "failed"
        notification.save(update_fields=["status"])
        return False

    try:
        result = send_teams_message(notification)
        if not result:
            notification.status = "failed"
            notification.save(update_fields=["status"])
        return result
    except Exception:
        notification.status = "failed"
        notification.save(update_fields=["status"])
        return False
