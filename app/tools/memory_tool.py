from datetime import datetime

from app.database.database import get_connection


def save_request_memory(
    customer_id: str,
    customer_email: str,
    message: str,
    analysis,
    task_id: str | None = None
):
    """
    Save a processed customer request and its analysis
    into persistent SQLite memory.
    """

    connection = get_connection()

    connection.execute(
        """
        INSERT INTO request_memory (
            customer_id,
            customer_email,
            message,
            category,
            priority,
            team,
            summary,
            task_id,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            customer_id,
            customer_email,
            message,
            analysis.category,
            analysis.priority,
            analysis.team,
            analysis.summary,
            task_id,
            datetime.now().isoformat()
        )
    )

    connection.commit()
    connection.close()


def get_customer_memories(
    customer_id: str,
    limit: int = 5
) -> list:
    """
    Return recent requests belonging to one customer.
    """

    connection = get_connection()

    rows = connection.execute(
        """
        SELECT *
        FROM request_memory
        WHERE customer_id = ?
        ORDER BY id DESC
        LIMIT ?
        """,
        (
            customer_id,
            limit
        )
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


def find_similar_request(
    customer_id: str,
    message: str
):
    """
    Detect an exact repeated request for the same customer.

    Comparison is case-insensitive and ignores
    leading/trailing whitespace.
    """

    connection = get_connection()

    row = connection.execute(
        """
        SELECT *
        FROM request_memory
        WHERE customer_id = ?
        AND LOWER(TRIM(message)) = LOWER(TRIM(?))
        ORDER BY id DESC
        LIMIT 1
        """,
        (
            customer_id,
            message
        )
    ).fetchone()

    connection.close()

    if row is None:
        return None

    return dict(row)