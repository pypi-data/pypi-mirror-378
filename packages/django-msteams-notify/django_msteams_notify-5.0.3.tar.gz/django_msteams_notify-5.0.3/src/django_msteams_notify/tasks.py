from celery import shared_task
from django_tenants.utils import schema_context
from django_msteams_notify.models import TeamsNotification
from django_msteams_notify.utils import send_teams_message

@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_teams_notification_task(self, tenant_schema_name, notification_id):
    try:
        # Switch to the correct tenant schema
        with schema_context(tenant_schema_name):
            notification = TeamsNotification.objects.get(id=notification_id)
            success = send_teams_message(notification)
            return success
    except TeamsNotification.DoesNotExist:
        return "deleted"
    except Exception as e:
        raise self.retry(exc=e)
