import os
import time

import resend
from dotenv import load_dotenv

from app.tools.audit_tool import log_event


load_dotenv()


def generate_email_draft(task: dict) -> dict:
    """
    Generate the customer email content.
    """

    subject = f"Update on your request - {task['task_id']}"

    draft = (
        f"Hello,\n\n"
        f"We have received your request regarding "
        f"{task['category'].lower()}.\n"
        f"Our {task['team']} is reviewing it with "
        f"{task['priority'].lower()} priority.\n"
        f"Your Task ID is {task['task_id']}.\n\n"
        f"Thank you."
    )

    return {
        "status": "Email Draft Generated",
        "subject": subject,
        "draft": draft
    }


def send_customer_email(
    task: dict,
    max_retries: int = 3
) -> dict:
    """
    Send the customer email using Resend.

    Retries temporary failures up to max_retries times.
    """

    email_enabled = os.getenv(
        "EMAIL_ENABLED",
        "false"
    ).lower() == "true"

    # Generate draft first
    email_draft = generate_email_draft(task)

    if not email_enabled:
        return {
            **email_draft,
            "delivery_status": "Email sending disabled"
        }

    api_key = os.getenv("RESEND_API_KEY")

    if not api_key:
        log_event(
            "EMAIL_FAILED",
            {
                "task_id": task["task_id"],
                "reason": "RESEND_API_KEY not configured"
            }
        )

        return {
            **email_draft,
            "delivery_status": "Failed",
            "error": "Email service is not configured"
        }

    resend.api_key = api_key

    recipient = task.get("customer_email")

    if not recipient:
        log_event(
            "EMAIL_FAILED",
            {
                "task_id": task["task_id"],
                "reason": "Customer email missing"
            }
        )

        return {
            **email_draft,
            "delivery_status": "Failed",
            "error": "Customer email is missing"
        }

    for attempt in range(1, max_retries + 1):

        try:
            response = resend.Emails.send(
                {
                    "from": (
                        "AI Operations Agent "
                        "<onboarding@resend.dev>"
                    ),
                    "to": [recipient],
                    "subject": email_draft["subject"],
                    "text": email_draft["draft"]
                }
            )

            log_event(
                "EMAIL_SENT",
                {
                    "task_id": task["task_id"],
                    "recipient": recipient,
                    "attempt": attempt
                }
            )

            return {
                **email_draft,
                "delivery_status": "Sent",
                "recipient": recipient,
                "attempts": attempt
            }

        except Exception as error:

            if attempt < max_retries:
                time.sleep(1)

            else:
                log_event(
                    "EMAIL_FAILED",
                    {
                        "task_id": task["task_id"],
                        "recipient": recipient,
                        "attempts": attempt,
                        "reason": str(error)
                    }
                )

                return {
                    **email_draft,
                    "delivery_status": "Failed",
                    "recipient": recipient,
                    "attempts": attempt,
                    "error": str(error)
                }