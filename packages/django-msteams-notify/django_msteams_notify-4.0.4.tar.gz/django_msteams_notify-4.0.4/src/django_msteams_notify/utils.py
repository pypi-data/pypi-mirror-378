import requests
from django.conf import settings
from django_msteams_notify.models import TeamsNotification

def send_teams_message(notification: TeamsNotification) -> bool:
    webhook_url = getattr(settings, "TEAMS_WEBHOOK_URL", None)

    if not webhook_url:
        notification.status = "failed"
        notification.message += "\n[Error: TEAMS_WEBHOOK_URL not set]"
        notification.save(update_fields=["status", "message"])
        print("[DEBUG] TEAMS_WEBHOOK_URL not set")
        return False

    try:
        payload = {"text": notification.message}
        response = requests.post(webhook_url, json=payload)
        print(f"[DEBUG] Teams response: {response.status_code} - {response.text}")  # debug

        if response.status_code == 200:
            notification.status = "sent"
            notification.save(update_fields=["status", "message"])
            return True  # return True immediately on success
        else:
            notification.status = "failed"
            notification.message += f"\n[Error: HTTP {response.status_code} - {response.text}]"

    except Exception as e:
        notification.status = "failed"
        notification.message += f"\n[Error: Exception {str(e)}]"
        print(f"[DEBUG] Exception sending Teams message: {str(e)}")  # debug

    notification.save(update_fields=["status", "message"])
    return False  # return False only if failure
