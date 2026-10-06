from app.models.request import RequestAnalysis
from app.providers.llm_provider import analyze_with_llm


def analyze_locally(message: str) -> RequestAnalysis:
    """
    Deterministic fallback analyzer.
    Used when an external LLM is unavailable.
    """

    text = message.lower()

    # Billing / payment requests
    if any(word in text for word in [
        "payment", "charged", "card", "refund", "billing"
    ]):
        category = "Billing"
        team = "Billing Team"

    # Technical requests
    elif any(word in text for word in [
        "error", "bug", "login", "crash", "technical"
    ]):
        category = "Technical"
        team = "Technical Support Team"

    # Account requests
    elif any(word in text for word in [
        "account", "password", "profile"
    ]):
        category = "Account"
        team = "Account Support Team"

    else:
        category = "General"
        team = "Support Team"

    # Determine priority
    if any(word in text for word in [
        "urgent", "immediately", "critical", "asap"
    ]):
        priority = "High"
    else:
        priority = "Medium"

    return RequestAnalysis(
        category=category,
        priority=priority,
        team=team,
        summary=message,
        action=f"Forward request to {team}"
    )


def analyze_request(message: str) -> RequestAnalysis:
    """
    Try the configured LLM first.
    If unavailable, safely use the local analyzer.
    """

    try:
        llm_result = analyze_with_llm(message)

        if llm_result is not None:
            return llm_result

    except Exception as error:
        print(f"LLM unavailable. Using local fallback: {error}")

    return analyze_locally(message)