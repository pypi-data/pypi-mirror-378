import requests
from django.conf import settings
from django_msteams_notify.models import TeamsNotification

def send_teams_message(notification: TeamsNotification):
    """Send a Teams message and update notification status."""
    webhook_url = getattr(settings, "TEAMS_WEBHOOK_URL", None)

    if not webhook_url:
        notification.status = "failed"
        notification.save(update_fields=["status"])
        return False

    try:
        payload = {"text": notification.message}
        response = requests.post(webhook_url, json=payload)

        if response.status_code == 200:
            notification.status = "sent"
            notification.save(update_fields=["status"])
            return True
        else:
            notification.status = "failed"
            notification.save(update_fields=["status"])
            response.raise_for_status()  # Raise HTTPError for Celery retry

    except Exception as e:
        notification.status = "failed"
        notification.save(update_fields=["status"])
        raise e  # Raise for Celery retry
