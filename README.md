# Enterprise AI Operations Agent

An agentic AI workflow system built with FastAPI that analyzes customer requests, routes them to the appropriate team, creates and tracks operational tasks, manages human approval workflows, maintains customer request memory, sends customer email updates, and records workflow events for auditing.

The project demonstrates how AI-based request understanding can be combined with deterministic business logic, persistent storage, human-in-the-loop approvals, external service integration, and failure handling.

---

## Features

- AI-powered customer request analysis using Google Gemini
- Structured LLM output using Pydantic models
- Rule-based fallback when the external LLM is unavailable
- Automatic request categorization and priority assignment
- Intelligent routing to appropriate support teams
- SQLite-based persistent task storage
- Customer-specific request memory
- Duplicate request detection
- Human-in-the-loop approval workflow
- Task and workflow status tracking
- Customer email integration using Resend
- Retry and graceful failure handling for email delivery
- Internal team notification simulation
- Persistent audit logging
- Request and email validation
- REST API built with FastAPI
- Interactive Swagger API documentation
- Automated API tests using Pytest
- Docker configuration for containerized deployment

---

## System Architecture

```text
Customer Request
       |
       v
FastAPI Endpoint
       |
       v
Pydantic Validation
       |
       v
Customer Memory Lookup
       |
       v
Duplicate Request Detection
       |
       v
Gemini LLM Analyzer
       |
       +---- LLM Failure ----> Local Rule-Based Fallback
       |
       v
Structured Request Analysis
       |
       v
Router / Decision Agent
       |
       v
Task Creation
       |
       v
SQLite Persistence
       |
       v
Is Human Approval Required?
       |
   +---+---+
   |       |
  Yes      No
   |       |
   v       |
WAITING    |
FOR        |
APPROVAL   |
   |       |
   v       |
Human      |
Decision   |
   |       |
Approve /  |
Reject     |
   |       |
   +---+---+
       |
       v
Internal Notification
       |
       v
Customer Email via Resend
       |
       v
Audit Logging
       |
       v
Workflow Completion
```

---

## Workflow

### 1. Request Validation

A customer sends a request containing:

- Customer ID
- Customer email
- Request message

FastAPI and Pydantic validate the incoming request before it enters the workflow.

---

### 2. Customer Memory and Duplicate Detection

The system checks previous requests stored for the same customer.

Exact duplicate messages are detected using customer-specific request history stored in SQLite.

Duplicate detection is scoped using the customer ID so identical requests from different customers are not incorrectly treated as duplicates.

A duplicate request is recorded in the audit log but may still create a new task because a repeated customer request can represent a legitimate follow-up.

---

### 3. AI Request Analysis

The request is first analyzed using Google Gemini.

The AI returns structured information including:

- Category
- Priority
- Responsible team
- Summary
- Recommended action

The response is validated using a Pydantic schema.

If Gemini is unavailable or an external API error occurs, the system automatically falls back to a deterministic local rule-based analyzer.

---

### 4. Routing and Decision Making

The routing component uses the request analysis to determine actions such as:

- Whether a task should be created
- Whether an internal notification should be generated
- Whether a customer email should be generated
- Whether human approval is required

This keeps AI-based understanding separate from deterministic workflow decisions.

---

### 5. Task Creation

Operational tasks are created with information including:

- Task ID
- Customer ID
- Customer email
- Category
- Priority
- Assigned team
- Business task status
- Workflow status
- Creation timestamp

Tasks are persisted in SQLite.

---

### 6. Human Approval Workflow

Certain requests can require human approval before downstream actions continue.

The workflow enters:

```text
WAITING_FOR_APPROVAL
```

A human can approve or reject the request through the approval API.

If approved, the workflow resumes.

If rejected, the workflow is marked as:

```text
REJECTED
```

Already processed approvals are protected against repeated processing.

---

### 7. Internal Notification

The system generates an internal team notification based on the task and assigned team.

The current implementation simulates this notification rather than connecting to a production Slack or Microsoft Teams workspace.

---

### 8. Customer Email

Customer email updates are integrated using Resend.

The system:

1. Generates the email content
2. Attempts delivery through the Resend API
3. Retries failed delivery attempts
4. Records successful or failed delivery events
5. Returns delivery information without crashing the overall API workflow

Email delivery can also be disabled using environment configuration.

---

### 9. Audit Logging

Important workflow events are stored in SQLite.

Examples include:

- Workflow completion
- Approval updates
- Workflow rejection
- Duplicate request detection
- Task status updates
- Email delivery success or failure

This provides traceability across workflow execution.

---

## Tech Stack

| Component | Technology |
|---|---|
| Programming Language | Python |
| API Framework | FastAPI |
| Data Validation | Pydantic |
| AI / LLM | Google Gemini |
| Database | SQLite |
| Email Integration | Resend |
| Testing | Pytest |
| API Testing | FastAPI TestClient / HTTPX |
| Environment Management | python-dotenv |
| Containerization | Docker |
| API Documentation | Swagger / OpenAPI |

---

## Project Structure

```text
AI OPT AGENT/
|
├── app/
│   ├── agents/
│   │   ├── request_analyzer.py
│   │   └── router_agent.py
│   │
│   ├── database/
│   │   └── database.py
│   │
│   ├── models/
│   │   └── request.py
│   │
│   ├── providers/
│   │   └── llm_provider.py
│   │
│   ├── tools/
│   │   ├── approval_tool.py
│   │   ├── audit_tool.py
│   │   ├── email_tool.py
│   │   ├── memory_tool.py
│   │   ├── notification_tool.py
│   │   └── task_tool.py
│   │
│   ├── workflow/
│   │   ├── approval_workflow.py
│   │   ├── orchestrator.py
│   │   └── state.py
│   │
│   └── main.py
│
├── tests/
│   ├── __init__.py
│   └── test_api.py
│
├── data/
├── .env.example
├── .gitignore
├── .dockerignore
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## API Endpoints

### Health and Service

```http
GET /
GET /health
```

### Request Processing

```http
POST /analyze
```

Example request:

```json
{
  "customer_id": "CUST-1001",
  "customer_email": "customer@example.com",
  "message": "The application crashes every time I open my profile."
}
```

### Task Management

```http
GET /tasks
GET /tasks/{task_id}
PATCH /tasks/{task_id}
```

Supported task statuses:

```text
Open
In Progress
Resolved
```

### Approval Management

```http
GET /approvals/{approval_id}
PATCH /approvals/{approval_id}
```

Supported approval decisions:

```text
Approved
Rejected
```

### Audit History

```http
GET /audit-logs
```

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd enterprise-ai-operations-agent
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Create a `.env` file in the project root.

Example:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key

RESEND_API_KEY=your_resend_api_key
EMAIL_ENABLED=true
```

A safe template is provided in:

```text
.env.example
```

The actual `.env` file is excluded from Git to prevent API keys from being committed.

For local rule-based analysis without Gemini:

```env
LLM_PROVIDER=local
EMAIL_ENABLED=false
```

---

## Running the Application

Start the FastAPI development server:

```bash
uvicorn app.main:app --reload
```

Open the interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

---

## Automated Testing

Run the automated API tests using:

```bash
pytest -v
```

The current API test suite validates areas including:

- Home endpoint
- Health endpoint
- Request validation
- Invalid email handling
- Missing customer information
- Unknown task handling
- Task status validation
- Unknown approval handling
- Approval status validation
- Audit log endpoint

Current local test result:

```text
10 passed
```

External Gemini and Resend calls are kept separate from these API validation tests to avoid unnecessary external API usage during routine test execution.

---

## Docker

The project includes:

```text
Dockerfile
.dockerignore
```

Build the image:

```bash
docker build -t ai-operations-agent .
```

Run with environment variables:

```bash
docker run --env-file .env -p 8000:8000 ai-operations-agent
```

Docker configuration is included for reproducible containerized execution. Local Docker execution should be verified in an environment with Docker installed.

---

## Reliability and Failure Handling

The project includes multiple failure-handling mechanisms:

**LLM failure**

```text
Gemini unavailable
        ↓
Local rule-based analyzer
        ↓
Workflow continues
```

**Email failure**

```text
Email attempt
     ↓
Failure
     ↓
Retry
     ↓
Failure recorded in audit log
```

The email integration handles delivery failures without crashing the complete API request.

---

## Security Considerations

- API keys are stored using environment variables
- `.env` is excluded from version control
- Input data is validated using Pydantic
- Runtime database files are excluded from Git
- Approval states are validated
- Invalid resource requests return appropriate HTTP errors

For a production deployment, authentication, authorization, secret management, rate limiting, and stronger access controls would be required.

---

## Current Limitations

This project is an industry-style educational implementation and is not presented as a production deployment.

Current limitations include:

- SQLite is used instead of a production database such as PostgreSQL
- Internal team notifications are simulated
- Duplicate detection currently uses normalized exact-message matching rather than vector-based semantic similarity
- Production authentication and RBAC are not implemented
- Resend testing/domain restrictions depend on account configuration
- Distributed background workers and message queues are not implemented
- Docker configuration is included but local Docker execution requires Docker to be installed

---

## Future Improvements

Possible extensions include:

- PostgreSQL database
- Redis caching
- Celery or another background job queue
- Semantic duplicate detection using embeddings
- Slack or Microsoft Teams integration
- Jira integration
- Authentication and role-based access control
- Metrics and observability dashboards
- Distributed workflow execution
- CI/CD pipeline
- Cloud deployment
- Advanced retry policies and idempotency
- Vector database for long-term semantic memory

---

## Purpose

The project demonstrates practical concepts used in AI-enabled backend systems:

- LLM integration
- Structured AI outputs
- Agentic workflow orchestration
- Human-in-the-loop decision making
- Persistent state and memory
- External API integration
- Failure handling
- REST API development
- Automated testing
- Auditability
- Containerization

It is designed as a portfolio and learning project for AI/ML engineering, backend engineering, and agentic AI development.