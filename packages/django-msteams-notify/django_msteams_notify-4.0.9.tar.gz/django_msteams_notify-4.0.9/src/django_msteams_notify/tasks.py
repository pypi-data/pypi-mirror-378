from celery import shared_task
from django_msteams_notify.models import TeamsNotification
from django_msteams_notify.utils import send_teams_message

@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_teams_notification_task(self, notification_id):
    try:
        notification = TeamsNotification.objects.get(id=notification_id)
        send_teams_message(notification)
        # Always return the actual status from the DB
        return notification.status
    except TeamsNotification.DoesNotExist:
        return "deleted"
    except Exception as e:
        raise self.retry(exc=e)
