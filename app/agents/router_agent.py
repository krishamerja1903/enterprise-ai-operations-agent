def decide_actions(analysis) -> dict:
    """
    Decide which actions should be performed
    based on the analyzed customer request.
    """

    actions = {
        "create_task": True,
        "send_notification": False,
        "generate_email": True,
        "requires_approval": False
    }

    # High-priority requests should notify the assigned team
    if analysis.priority == "High":
        actions["send_notification"] = True

    # Billing issues may involve sensitive business actions,
    # so they require human approval
    if analysis.category == "Billing":
        actions["requires_approval"] = True

    return actions