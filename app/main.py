from fastapi import FastAPI, HTTPException

from app.database.database import initialize_database

from app.models.request import (
    CustomerRequest,
    TaskStatusUpdate,
    ApprovalUpdate
)

from app.tools.task_tool import (
    get_all_tasks,
    get_task,
    update_task_status
)

from app.tools.approval_tool import (
    get_approval,
    update_approval
)

from app.tools.audit_tool import (
    log_event,
    get_audit_logs
)

from app.workflow.orchestrator import run_workflow
from app.workflow.approval_workflow import handle_approval_result


# -------------------------------------------------
# FASTAPI APPLICATION
# -------------------------------------------------

app = FastAPI(
    title="Enterprise AI Operations Agent",
    description=(
        "Agentic AI system for analyzing enterprise customer "
        "requests, routing work, managing approvals, and "
        "maintaining an audit trail."
    ),
    version="1.0.0"
)

# Initialize SQLite database and tables
initialize_database()


# -------------------------------------------------
# HOME
# -------------------------------------------------

@app.get(
    "/",
    summary="API home"
)
def home():

    return {
        "message": "Enterprise AI Operations Agent is running"
    }


# -------------------------------------------------
# HEALTH CHECK
# -------------------------------------------------

@app.get(
    "/health",
    summary="Check API health"
)
def health_check():

    return {
        "status": "healthy"
    }


# -------------------------------------------------
# MAIN AGENT WORKFLOW
# -------------------------------------------------

@app.post(
    "/analyze",
    summary="Analyze and process a customer request",
    responses={
        422: {
            "description": "Invalid request data"
        }
    }
)
def analyze_customer_request(
    request: CustomerRequest
):

    result = run_workflow(
        message=request.message,
        customer_id=request.customer_id,
        customer_email=str(request.customer_email)
    )

    return {
        **result,
        "status": "Request processed successfully"
    }


# -------------------------------------------------
# TASK MANAGEMENT
# -------------------------------------------------

@app.get(
    "/tasks",
    summary="View all tasks"
)
def view_all_tasks():

    return {
        "tasks": get_all_tasks()
    }


@app.get(
    "/tasks/{task_id}",
    summary="View a task",
    responses={
        404: {
            "description": "Task not found"
        }
    }
)
def view_task(task_id: str):

    task = get_task(task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


@app.patch(
    "/tasks/{task_id}",
    summary="Update task status",
    responses={
        404: {
            "description": "Task not found"
        },
        422: {
            "description": "Invalid task status"
        }
    }
)
def change_task_status(
    task_id: str,
    update: TaskStatusUpdate
):

    task = update_task_status(
        task_id,
        update.status
    )

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    log_event(
        "TASK_STATUS_UPDATED",
        {
            "task_id": task_id,
            "status": update.status
        }
    )

    return {
        "message": "Task status updated successfully",
        "task": task
    }


# -------------------------------------------------
# HUMAN APPROVAL
# -------------------------------------------------

@app.get(
    "/approvals/{approval_id}",
    summary="View an approval request",
    responses={
        404: {
            "description": "Approval not found"
        }
    }
)
def view_approval(approval_id: str):

    approval = get_approval(
        approval_id
    )

    if approval is None:
        raise HTTPException(
            status_code=404,
            detail="Approval not found"
        )

    return approval


@app.patch(
    "/approvals/{approval_id}",
    summary="Approve or reject a pending workflow",
    responses={
        404: {
            "description": "Approval not found"
        },
        409: {
            "description": "Approval already processed"
        },
        422: {
            "description": "Invalid approval status"
        }
    }
)
def change_approval_status(
    approval_id: str,
    update: ApprovalUpdate
):

    approval = update_approval(
        approval_id,
        update.status
    )

    if approval is None:
        raise HTTPException(
            status_code=404,
            detail="Approval not found"
        )

    if approval.get("already_processed"):
        raise HTTPException(
            status_code=409,
            detail="Approval has already been processed"
        )

    # Remove internal helper flag from API response
    approval.pop(
        "already_processed",
        None
    )

    log_event(
        "APPROVAL_UPDATED",
        {
            "approval_id": approval_id,
            "task_id": approval["task_id"],
            "status": update.status
        }
    )

    workflow_result = handle_approval_result(
        approval
    )

    return {
        "message": "Approval processed successfully",
        "approval": approval,
        "workflow": workflow_result
    }


# -------------------------------------------------
# AUDIT LOGS
# -------------------------------------------------

@app.get(
    "/audit-logs",
    summary="View workflow audit history"
)
def view_audit_logs():

    return {
        "audit_logs": get_audit_logs()
    }