from datetime import datetime
import random

email_events = []


def send_email(to_email, subject, body):

    # Simulate delivery success
    delivered = random.random() > 0.05  # 95% success rate

    if not delivered:
        return {
            "email": to_email,
            "opened": False,
            "replied": False,
            "time": datetime.now().strftime("%H:%M:%S"),
            "status": "failed"
        }

    # Simulate engagement based on simple logic
    opened = random.random() > 0.3   # 70% open rate
    replied = opened and (random.random() > 0.6)  # ~40% reply if opened

    event = {
        "email": to_email,
        "opened": opened,
        "replied": replied,
        "time": datetime.now().strftime("%H:%M:%S"),
        "status": "sent"
    }

    email_events.append(event)

    return event


def get_email_events():
    return email_events[-10:]