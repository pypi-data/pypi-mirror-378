from celery import shared_task
from django_msteams_notify.models import TeamsNotification
from django_msteams_notify.utils import send_teams_message

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=5)
def send_teams_notification_task(self, notification_id):
    try:
        notification = TeamsNotification.objects.get(id=notification_id)
    except TeamsNotification.DoesNotExist:
        # Stop if the notification truly doesn't exist
        return False

    success = send_teams_message(notification)
    if not success:
        raise Exception(f"Failed to send Teams notification ID {notification_id}")

    return True
