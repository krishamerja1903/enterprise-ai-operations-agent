import json
from datetime import datetime

from app.database.database import get_connection


def log_event(
    event_type: str,
    event_data: dict
):

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO audit_logs (
            event_type,
            event_data,
            created_at
        )
        VALUES (?, ?, ?)
        """,
        (
            event_type,
            json.dumps(event_data),
            datetime.now().isoformat()
        )
    )

    connection.commit()
    connection.close()


def get_audit_logs() -> list:

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM audit_logs
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    logs = []

    for row in rows:
        log = dict(row)

        try:
            log["event_data"] = json.loads(
                log["event_data"]
            )
        except json.JSONDecodeError:
            pass

        logs.append(log)

    return logs