import uuid
from datetime import datetime

from app.database.database import get_connection


def create_approval(task: dict) -> dict:

    approval = {
        "approval_id": f"APR-{uuid.uuid4().hex[:6].upper()}",
        "task_id": task["task_id"],
        "action": "Review sensitive billing request",
        "status": "Pending",
        "created_at": datetime.now().isoformat(),
        "updated_at": None
    }

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO approvals (
            approval_id,
            task_id,
            action,
            status,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            approval["approval_id"],
            approval["task_id"],
            approval["action"],
            approval["status"],
            approval["created_at"],
            approval["updated_at"]
        )
    )

    connection.commit()
    connection.close()

    return approval


def get_approval(approval_id: str):

    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM approvals
        WHERE approval_id = ?
        """,
        (approval_id,)
    ).fetchone()

    connection.close()

    if row is None:
        return None

    return dict(row)


def update_approval(
    approval_id: str,
    status: str
):

    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM approvals
        WHERE approval_id = ?
        """,
        (approval_id,)
    ).fetchone()

    if row is None:
        connection.close()
        return None

    approval = dict(row)

    # Idempotency protection
    if approval["status"] != "Pending":
        connection.close()

        return {
            **approval,
            "already_processed": True
        }

    updated_at = datetime.now().isoformat()

    connection.execute(
        """
        UPDATE approvals
        SET status = ?, updated_at = ?
        WHERE approval_id = ?
        """,
        (
            status,
            updated_at,
            approval_id
        )
    )

    connection.commit()
    connection.close()

    approval = get_approval(approval_id)

    return {
        **approval,
        "already_processed": False
    }