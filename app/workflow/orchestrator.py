from app.agents.request_analyzer import analyze_request
from app.agents.router_agent import decide_actions

from app.tools.task_tool import (
    create_task,
    update_workflow_status
)
from app.tools.notification_tool import send_notification
from app.tools.email_tool import send_customer_email
from app.tools.approval_tool import create_approval
from app.tools.audit_tool import log_event

from app.tools.memory_tool import (
    save_request_memory,
    find_similar_request
)

from app.workflow.state import WorkflowState


def run_workflow(
    message: str,
    customer_id: str,
    customer_email: str
) -> WorkflowState:

    state: WorkflowState = {
        "message": message,
        "customer_id": customer_id,
        "customer_email": customer_email
    }

    # -------------------------------------------------
    # 1. CHECK CUSTOMER MEMORY
    # -------------------------------------------------

    previous_request = find_similar_request(
        customer_id=customer_id,
        message=message
    )

    state["duplicate_request"] = (
        previous_request is not None
    )

    state["previous_request"] = previous_request

    # -------------------------------------------------
    # 2. ANALYZE REQUEST
    # -------------------------------------------------

    analysis = analyze_request(message)

    state["analysis"] = analysis

    # -------------------------------------------------
    # 3. DECIDE REQUIRED ACTIONS
    # -------------------------------------------------

    decisions = decide_actions(analysis)

    state["decisions"] = decisions

    # -------------------------------------------------
    # 4. CREATE TASK
    # -------------------------------------------------

    task = None

    if decisions["create_task"]:

        task = create_task(
            message=message,
            analysis=analysis,
            customer_id=customer_id,
            customer_email=customer_email
        )

    state["task"] = task

    # -------------------------------------------------
    # 5. SAVE REQUEST TO MEMORY
    # -------------------------------------------------

    if task:

        save_request_memory(
            customer_id=customer_id,
            customer_email=customer_email,
            message=message,
            analysis=analysis,
            task_id=task["task_id"]
        )

    # -------------------------------------------------
    # 6. RECORD DUPLICATE DETECTION
    # -------------------------------------------------

    if previous_request:

        log_event(
            "DUPLICATE_REQUEST_DETECTED",
            {
                "customer_id": customer_id,
                "new_task_id": (
                    task["task_id"]
                    if task
                    else None
                ),
                "previous_task_id": (
                    previous_request["task_id"]
                )
            }
        )

    # -------------------------------------------------
    # 7. HUMAN APPROVAL GATE
    # -------------------------------------------------

    approval = None

    if (
        decisions["requires_approval"]
        and task
    ):

        approval = create_approval(task)

        task = update_workflow_status(
            task["task_id"],
            "WAITING_FOR_APPROVAL"
        )

        state["task"] = task
        state["approval"] = approval
        state["notification"] = None
        state["email_draft"] = None

        log_event(
            "WAITING_FOR_APPROVAL",
            {
                "task_id": task["task_id"],
                "approval_id": approval["approval_id"],
                "customer_id": customer_id
            }
        )

        return state

    state["approval"] = None

    # -------------------------------------------------
    # 8. SEND TEAM NOTIFICATION
    # -------------------------------------------------

    notification = None

    if (
        decisions["send_notification"]
        and task
    ):
        notification = send_notification(task)

    state["notification"] = notification

    # -------------------------------------------------
    # 9. SEND CUSTOMER EMAIL
    # -------------------------------------------------

    email_result = None

    if (
        decisions["generate_email"]
        and task
    ):
        email_result = send_customer_email(task)

    state["email_draft"] = email_result

    # -------------------------------------------------
    # 10. MARK WORKFLOW COMPLETE
    # -------------------------------------------------

    if task:

        task = update_workflow_status(
            task["task_id"],
            "COMPLETED"
        )

        state["task"] = task

        log_event(
            "WORKFLOW_COMPLETED",
            {
                "task_id": task["task_id"],
                "customer_id": customer_id
            }
        )

    return state