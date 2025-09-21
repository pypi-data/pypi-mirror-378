import requests
from django.conf import settings
from django_msteams_notify.models import TeamsNotification

def send_teams_message(notification: TeamsNotification) -> bool:
    """
    Send a Teams message and update status.
    Returns True if sent successfully, False otherwise.
    Stores failure reason in the message field.
    """
    webhook_url = getattr(settings, "TEAMS_WEBHOOK_URL", None)

    if not webhook_url:
        notification.status = "failed"
        notification.message += "\n[Error: TEAMS_WEBHOOK_URL not set]"
        notification.save(update_fields=["status", "message"])
        return False

    try:
        payload = {"text": notification.message}
        response = requests.post(webhook_url, json=payload)

        if response.status_code == 200:
            notification.status = "sent"
        else:
            notification.status = "failed"
            notification.message += f"\n[Error: HTTP {response.status_code} - {response.text}]"

    except Exception as e:
        notification.status = "failed"
        notification.message += f"\n[Error: Exception {str(e)}]"

    notification.save(update_fields=["status", "message"])
    return notification.status == "sent"
