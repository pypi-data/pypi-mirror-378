from celery import shared_task
from django_msteams_notify.models import TeamsNotification
from django_msteams_notify.utils import send_teams_message

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def send_teams_notification_task(self, notification_id):
    """Send a Teams notification asynchronously with retries."""
    try:
        notification = TeamsNotification.objects.get(id=notification_id)
    except TeamsNotification.DoesNotExist:
        return False  # Task finished if notification doesn't exist

    # Call utils function and raise exception if failed so Celery can retry
    success = send_teams_message(notification)
    if not success:
        raise Exception("Failed to send Teams notification")

    return True
