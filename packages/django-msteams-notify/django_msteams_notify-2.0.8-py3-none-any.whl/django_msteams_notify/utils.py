# utils.py
import requests
from django.conf import settings
from django_msteams_notify.models import TeamsNotification


def send_teams_message(notification: TeamsNotification) -> bool:
    webhook_url = getattr(settings, "TEAMS_WEBHOOK_URL", None)
    if not webhook_url:
        # If webhook not configured, mark as failed
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
            # Non-200 response, mark as failed and raise to trigger Celery retry
            notification.status = "failed"
            notification.save(update_fields=["status"])
            response.raise_for_status()

    except Exception:
        # Any exception marks the notification as failed and allows Celery retry
        notification.status = "failed"
        notification.save(update_fields=["status"])
        raise
