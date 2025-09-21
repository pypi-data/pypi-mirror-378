from celery import shared_task
from .utils import send_teams_message
from .models import TeamsNotification

@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_teams_notification_task(self, notification_id):
    try:
        notification = TeamsNotification.objects.get(id=notification_id)
        success = send_teams_message(notification)
        return success
    except Exception as e:
        raise self.retry(exc=e)
