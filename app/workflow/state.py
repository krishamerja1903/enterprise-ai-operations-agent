from typing import TypedDict, Optional, Any


class WorkflowState(TypedDict, total=False):
    message: str

    # Memory / duplicate detection
    duplicate_request: bool
    previous_request: Optional[dict]

    # AI analysis and routing
    analysis: Any
    decisions: dict

    # Workflow outputs
    task: Optional[dict]
    approval: Optional[dict]
    notification: Optional[dict]
    email_draft: Optional[dict]