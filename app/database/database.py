import sqlite3
from pathlib import Path


DATABASE_PATH = Path("data/operations.db")


def get_connection():
    """
    Create and return a SQLite database connection.
    """

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def add_column_if_missing(
    cursor,
    table_name: str,
    column_name: str,
    column_definition: str
):
    """
    Add a column to an existing SQLite table
    only if the column does not already exist.
    """

    columns = cursor.execute(
        f"PRAGMA table_info({table_name})"
    ).fetchall()

    existing_columns = [
        column["name"]
        for column in columns
    ]

    if column_name not in existing_columns:
        cursor.execute(
            f"""
            ALTER TABLE {table_name}
            ADD COLUMN {column_name} {column_definition}
            """
        )


def initialize_database():
    """
    Create database tables and apply small schema migrations.
    """

    connection = get_connection()
    cursor = connection.cursor()

    # -------------------------------------------------
    # TASKS
    # -------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            customer_id TEXT,
            customer_email TEXT,
            message TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            team TEXT NOT NULL,
            status TEXT NOT NULL,
            workflow_status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    # Add fields safely for databases created by older versions
    add_column_if_missing(
        cursor,
        "tasks",
        "customer_id",
        "TEXT"
    )

    add_column_if_missing(
        cursor,
        "tasks",
        "customer_email",
        "TEXT"
    )

    # -------------------------------------------------
    # APPROVALS
    # -------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS approvals (
            approval_id TEXT PRIMARY KEY,
            task_id TEXT NOT NULL,
            action TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT,
            FOREIGN KEY (task_id)
                REFERENCES tasks(task_id)
        )
        """
    )

    # -------------------------------------------------
    # AUDIT LOGS
    # -------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            event_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    # -------------------------------------------------
    # REQUEST MEMORY
    # -------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS request_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            customer_email TEXT,
            message TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            team TEXT NOT NULL,
            summary TEXT NOT NULL,
            task_id TEXT,
            created_at TEXT NOT NULL,
            FOREIGN KEY (task_id)
                REFERENCES tasks(task_id)
        )
        """
    )

    # Add fields safely for existing request_memory table
    add_column_if_missing(
        cursor,
        "request_memory",
        "customer_id",
        "TEXT"
    )

    add_column_if_missing(
        cursor,
        "request_memory",
        "customer_email",
        "TEXT"
    )

    connection.commit()
    connection.close()