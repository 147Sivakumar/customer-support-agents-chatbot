
import json
import os

from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()


async def generate_resolution(
    complaint: str,
    query_analysis: dict,
    knowledge_result: dict,
) -> dict:
    """Generate a customer reply grounded in retrieved company policies."""

    if not complaint or not complaint.strip():
        raise ValueError("Customer complaint cannot be empty.")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY is missing. Configure it in your .env file."
        )

    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        api_key=api_key,
    )

    agent = AssistantAgent(
        name="resolution_agent",
        model_client=model_client,
        system_message="""
You are the Resolution Agent for an online store.

Write a clear, polite, helpful reply to the customer.

Rules:
1. Use only facts supported by the supplied knowledge-base passages.
2. Never invent company policies, delivery dates, refund approvals,
   product features, or actions that have not happened.
3. If no relevant knowledge-base passage was found, explain that the
   issue needs review by human support.
4. If the policy says support must review a case, do not promise an outcome.
5. Never ask customers to share passwords.
6. Recommend escalation for high urgency, angry customers, legal threats,
   suspected fraud, payment disputes, missing policy information, or low
   confidence.
7. Return only valid JSON with these keys:
   response, confidence, escalation_recommended, escalation_reason.
8. confidence must be a number from 0 to 1.
9. escalation_recommended must be true or false.
10. escalation_reason must be a short string, or an empty string when
    escalation is not recommended.
""",
    )

    task_data = {
        "customer_complaint": complaint,
        "query_analysis": query_analysis,
        "knowledge_base_result": knowledge_result,
    }

    try:
        result = await agent.run(
            task=(
                "Draft a grounded customer-support response using this data. "
                "Return the required JSON only.\n\n"
                + json.dumps(task_data, ensure_ascii=False)
            )
        )

        content = result.messages[-1].content

        if not isinstance(content, str):
            raise ValueError("The agent returned an unexpected response.")

        content = content.strip()

        if not content:
            raise ValueError(
                "Resolution Agent returned an empty response. "
                "Please try submitting the complaint again."
            )

        # Handle responses wrapped in Markdown JSON code fences.
        if content.startswith("```"):
            lines = content.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            content = "\n".join(lines).strip()

        try:
            data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "Resolution Agent returned invalid JSON. "
                f"Response received: {content[:500]!r}"
            ) from exc

        required_keys = {
            "response",
            "confidence",
            "escalation_recommended",
            "escalation_reason",
        }
        if not required_keys.issubset(data):
            raise ValueError("The agent response is missing required fields.")

        confidence = float(data["confidence"])
        if not 0 <= confidence <= 1:
            raise ValueError("Confidence must be between 0 and 1.")

        if not isinstance(data["escalation_recommended"], bool):
            raise ValueError("Escalation recommendation must be true or false.")

        # Apply mandatory escalation rules in code as a safety check.
        urgency = query_analysis.get("urgency", "")
        sentiment = query_analysis.get("sentiment", "")
        complaint_lower = complaint.lower()

        risk_terms = (
            "legal",
            "lawyer",
            "lawsuit",
            "fraud",
            "unauthorized payment",
            "payment dispute",
            "chargeback",
        )

        mandatory_escalation = (
            urgency == "High"
            or sentiment == "Angry"
            or not knowledge_result.get("found", False)
            or confidence < 0.6
            or any(term in complaint_lower for term in risk_terms)
        )

        if mandatory_escalation:
            data["escalation_recommended"] = True
            if not data["escalation_reason"]:
                data["escalation_reason"] = (
                    "Requires human review due to risk, missing policy "
                    "information, or low resolution confidence."
                )

        data["confidence"] = confidence
        return data

    finally:
        await model_client.close()
