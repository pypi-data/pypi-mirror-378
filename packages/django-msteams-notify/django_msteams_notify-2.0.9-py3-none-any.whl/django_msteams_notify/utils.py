import requests
from django.conf import settings
from django_msteams_notify.models import TeamsNotification

def send_teams_message(notification: TeamsNotification):
    webhook_url = getattr(settings, "TEAMS_WEBHOOK_URL", None)
    if not webhook_url:
        notification.status = "failed"
        notification.save(update_fields=["status"])
        return False

    payload = {"text": notification.message}

    try:
        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            notification.status = "sent"
            notification.save(update_fields=["status"])
            return True
        else:
            notification.status = "failed"
            notification.save(update_fields=["status"])
            response.raise_for_status()  # Let Celery retry
    except Exception:
        notification.status = "failed"
        notification.save(update_fields=["status"])
        raise
