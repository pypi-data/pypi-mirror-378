from celery import shared_task
from django_msteams_notify.models import TeamsNotification
from django_msteams_notify.utils import send_teams_message

class TeamsNotificationSendError(Exception):
    """Custom exception to retry failed Teams messages."""
    pass

@shared_task(
    bind=True,
    autoretry_for=(TeamsNotificationSendError,),
    retry_backoff=True,
    max_retries=5,
)
def send_teams_notification_task(self, notification_id):
    from uuid import UUID
    try:
        notification = TeamsNotification.objects.get(id=UUID(notification_id))
    except (TeamsNotification.DoesNotExist, ValueError):
        return False

    success = send_teams_message(notification)
    if not success:
        raise TeamsNotificationSendError(f"Failed to send notification {notification.id}")

    return True
