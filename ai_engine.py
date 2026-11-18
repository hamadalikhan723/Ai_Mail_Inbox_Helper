
import json
import os
import re
import time

from google import genai
from google.genai.errors import ServerError


MODEL_NAME = "gemini-3.5-flash-lite"


def load_company_knowledge():
    with open("company_knowledge.json", "r", encoding="utf-8") as file:
        return json.load(file)


def generate_reply(client, message, company_context):
    prompt = f"""
You are an AI assistant helping the HR team at MUST Company.

COMPANY KNOWLEDGE:
{company_context}

CANDIDATE MESSAGE:
{message}

Instructions:
- Identify the candidate's main intent.
- Assign a short, clear category.
- Draft a short, polite, professional reply.
- Use only the supplied company knowledge.
- Never invent salary, interview dates, application status,
  working hours, benefits, or recruitment policies.
- If information is unavailable or candidate-specific,
  set review_status to "Needs HR Verification".
- Otherwise set review_status to "General Reply - Human Approval Required".
- Never claim HR has taken action or contacted the candidate.
- Never claim an application or CV has been updated or forwarded.
- Do not include internal review labels in the reply draft.
- Every reply must be reviewed by a human before use.
- Do not send emails.

Return ONLY valid JSON with these exact keys:
{{
  "category": "short category",
  "review_status": "Needs HR Verification or General Reply - Human Approval Required",
  "review_reason": "short explanation",
  "reply_draft": "the candidate-facing reply"
}}
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            cleaned = response.text.strip()
            cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
            cleaned = re.sub(r"\s*```$", "", cleaned)

            return json.loads(cleaned)

        except ServerError:
            if attempt == 2:
                raise
            time.sleep(3 * (attempt + 1))

        except (json.JSONDecodeError, AttributeError):
            if attempt == 2:
                raise
            time.sleep(2)

    raise RuntimeError("Could not generate a valid response.")
