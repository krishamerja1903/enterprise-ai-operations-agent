import os
from typing import Optional

from dotenv import load_dotenv
from google import genai

from app.models.request import RequestAnalysis


# Load variables from .env
load_dotenv()


def analyze_with_llm(message: str) -> Optional[RequestAnalysis]:
    """
    Analyze a customer request using the configured LLM provider.

    Returns None when local mode is selected.
    Raises an exception if the external provider fails so that
    request_analyzer.py can safely use the local fallback.
    """

    provider = os.getenv("LLM_PROVIDER", "local").lower()

    # Local mode -> request_analyzer.py will use rule-based fallback
    if provider == "local":
        return None

    if provider != "gemini":
        raise ValueError(f"Unsupported LLM provider: {provider}")

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError("GEMINI_API_KEY is not configured")

    client = genai.Client(api_key=api_key)

    prompt = f"""
You are an enterprise customer-support request analyzer.

Analyze the customer request and return structured information.

Rules:
- category must be one of: Billing, Technical, Account, General
- priority must be one of: High, Medium, Low
- team must correspond to the category:
  Billing -> Billing Team
  Technical -> Technical Support Team
  Account -> Account Support Team
  General -> Support Team
- summary should be a concise professional summary
- action should describe the recommended next action

Customer request:
{message}
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": RequestAnalysis,
        },
    )

    if response.parsed is None:
        raise ValueError("Gemini returned no structured analysis")

    return response.parsed