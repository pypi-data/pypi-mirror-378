import requests
from django.conf import settings
from django_msteams_notify.models import TeamsNotification

def send_teams_message(notification: TeamsNotification):
    webhook_url = getattr(settings, "TEAMS_WEBHOOK_URL", None)
    if not webhook_url:
        notification.status = "failed"
        notification.save(update_fields=["status"])
        return False

    try:
        response = requests.post(webhook_url, json={"text": notification.message})
        if response.status_code == 200:
            notification.status = "sent"
        else:
            notification.status = "failed"
            response.raise_for_status()
    except Exception:
        notification.status = "failed"
        raise
    finally:
        notification.save(update_fields=["status"])

    return notification.status == "sent"
