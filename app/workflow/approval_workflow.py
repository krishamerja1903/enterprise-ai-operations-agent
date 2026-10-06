from app.tools.task_tool import (
    get_task,
    update_workflow_status
)
from app.tools.notification_tool import send_notification
from app.tools.email_tool import send_customer_email
from app.tools.audit_tool import log_event


def handle_approval_result(approval: dict) -> dict:

    task = get_task(approval["task_id"])

    if task is None:
        return {
            "status": "FAILED",
            "message": "Associated task not found"
        }

    # -------------------------------------------------
    # HUMAN APPROVED THE REQUEST
    # -------------------------------------------------

    if approval["status"] == "Approved":

        notification = send_notification(task)

        email_result = send_customer_email(task)

        task = update_workflow_status(
            task["task_id"],
            "COMPLETED"
        )

        log_event(
            "APPROVED_WORKFLOW_COMPLETED",
            {
                "task_id": task["task_id"],
                "approval_id": approval["approval_id"]
            }
        )

        return {
            "workflow_status": "COMPLETED",
            "task": task,
            "notification": notification,
            "email": email_result
        }

    # -------------------------------------------------
    # HUMAN REJECTED THE REQUEST
    # -------------------------------------------------

    task = update_workflow_status(
        task["task_id"],
        "REJECTED"
    )

    log_event(
        "WORKFLOW_REJECTED",
        {
            "task_id": task["task_id"],
            "approval_id": approval["approval_id"]
        }
    )

    return {
        "workflow_status": "REJECTED",
        "task": task,
        "notification": None,
        "email": None
    }