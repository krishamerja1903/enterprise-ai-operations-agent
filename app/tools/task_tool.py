import uuid
from datetime import datetime

from app.database.database import get_connection


def create_task(
    message: str,
    analysis,
    customer_id: str,
    customer_email: str
) -> dict:

    task = {
        "task_id": f"TASK-{uuid.uuid4().hex[:6].upper()}",
        "customer_id": customer_id,
        "customer_email": customer_email,
        "message": message,
        "category": analysis.category,
        "priority": analysis.priority,
        "team": analysis.team,
        "status": "Open",
        "workflow_status": "PROCESSING",
        "created_at": datetime.now().isoformat()
    }

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO tasks (
            task_id,
            customer_id,
            customer_email,
            message,
            category,
            priority,
            team,
            status,
            workflow_status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            task["task_id"],
            task["customer_id"],
            task["customer_email"],
            task["message"],
            task["category"],
            task["priority"],
            task["team"],
            task["status"],
            task["workflow_status"],
            task["created_at"]
        )
    )

    connection.commit()
    connection.close()

    return task


def get_all_tasks() -> list:

    connection = get_connection()

    rows = connection.execute(
        "SELECT * FROM tasks ORDER BY created_at DESC"
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


def get_task(task_id: str):

    connection = get_connection()

    row = connection.execute(
        "SELECT * FROM tasks WHERE task_id = ?",
        (task_id,)
    ).fetchone()

    connection.close()

    if row is None:
        return None

    return dict(row)


def update_task_status(
    task_id: str,
    status: str
):

    connection = get_connection()

    cursor = connection.execute(
        """
        UPDATE tasks
        SET status = ?
        WHERE task_id = ?
        """,
        (status, task_id)
    )

    connection.commit()
    connection.close()

    if cursor.rowcount == 0:
        return None

    return get_task(task_id)


def update_workflow_status(
    task_id: str,
    workflow_status: str
):

    connection = get_connection()

    cursor = connection.execute(
        """
        UPDATE tasks
        SET workflow_status = ?
        WHERE task_id = ?
        """,
        (workflow_status, task_id)
    )

    connection.commit()
    connection.close()

    if cursor.rowcount == 0:
        return None

    return get_task(task_id)