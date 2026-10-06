from pydantic import BaseModel, Field, EmailStr
from typing import Literal


class CustomerRequest(BaseModel):
    customer_id: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique identifier for the customer"
    )

    customer_email: EmailStr = Field(
        ...,
        description="Customer email address"
    )

    message: str = Field(
        ...,
        min_length=3,
        max_length=1000,
        description="Customer request to be analyzed"
    )


class RequestAnalysis(BaseModel):
    category: str
    priority: str
    team: str
    summary: str
    action: str


class TaskStatusUpdate(BaseModel):
    status: Literal[
        "Open",
        "In Progress",
        "Resolved"
    ]


class ApprovalUpdate(BaseModel):
    status: Literal[
        "Approved",
        "Rejected"
    ]