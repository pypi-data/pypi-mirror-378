from celery import shared_task
from django_msteams_notify.models import TeamsNotification
from django_msteams_notify.utils import send_teams_message
from django.conf import settings
from uuid import UUID

class TeamsNotificationSendError(Exception):
    """Custom exception to trigger retry when Teams message fails."""
    pass

@shared_task(
    bind=True,
    autoretry_for=(TeamsNotificationSendError,),
    retry_backoff=True,
    max_retries=5,
)
def send_teams_notification_task(self, notification_id):
    """
    Send a Teams notification asynchronously with retries.
    Only retries if sending fails (status not 'sent').
    """
    try:
        notification = TeamsNotification.objects.get(id=UUID(notification_id))
    except (TeamsNotification.DoesNotExist, ValueError):
        return False

    # Make sure webhook URL exists
    if not getattr(settings, "TEAMS_WEBHOOK_URL", None):
        notification.status = "failed"
        notification.save(update_fields=["status"])
        return False

    # Send the message
    result = send_teams_message(notification)

    # If sending fails, raise custom exception to trigger retry
    if not result:
        raise TeamsNotificationSendError(f"Failed to send notification {notification.id}")

    return True
