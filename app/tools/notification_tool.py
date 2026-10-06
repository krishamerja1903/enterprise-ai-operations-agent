def send_notification(task: dict) -> dict:
    notification = (
        f"Task {task['task_id']} assigned to {task['team']} "
        f"with {task['priority']} priority."
    )

    print(f"\nTEAM NOTIFICATION: {notification}")

    return {
        "status": "Notification Sent",
        "message": notification
    }