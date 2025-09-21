from celery import shared_task
from django_msteams_notify.models import TeamsNotification
from django_msteams_notify.utils import send_teams_message

@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_teams_notification_task(self, notification_id):
    try:
        notification = TeamsNotification.objects.get(id=notification_id)
        success = send_teams_message(notification)
        return success  # True if sent, False if failed
    except TeamsNotification.DoesNotExist:
        # Object doesn't exist (should not happen if using transaction.on_commit)
        return "deleted"
    except Exception as e:
        raise self.retry(exc=e)
