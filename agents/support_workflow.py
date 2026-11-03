
import json
import os

from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from agents.knowledge_agent import search_kb
from agents.log_agent import log_ticket

load_dotenv()

DEPARTMENTS = {
    "IT": """
You are the IT Support Agent.
Handle login, passwords, software, computers, internet, email,
printers, access permissions, and technical problems.
Give simple, safe troubleshooting steps.
Never ask for passwords or secret keys.
""",
    "Admin": """
You are the Administration Support Agent.
Handle office facilities, ID cards, desks, equipment requests,
office access, housekeeping, and workplace maintenance.
Do not invent company policies or promise approvals.
""",
    "HR": """
You are the Human Resources Support Agent.
Handle leave, attendance, employee policies, onboarding,
workplace concerns, and employee documentation.
Protect employee privacy. Refer sensitive matters to HR staff.
Do not invent company policies or promise approvals.
""",
    "Accountant": """
You are the Accounts Support Agent.
Handle salary queries, payslips, reimbursements, invoices,
expense claims, and payment-related questions.
Never request bank passwords, PINs, or OTPs.
Do not promise payments or financial approvals.
""",
    "Complex Issues": """
You are the Complex Issues Support Agent.
Handle unclear requests, issues involving multiple departments,
serious complaints, suspected fraud, legal concerns, and unresolved issues.
Explain the next steps and recommend human review when appropriate.
Never make unsupported promises or decisions.
"""
}


def route_department(complaint: str) -> str:
    """Route a complaint without needing an extra AI agent."""
    text = complaint.lower()

    high_risk_terms = [
        "fraud", "lawsuit", "lawyer", "legal threat",
        "harassment", "data breach", "security breach",
        "unauthorized payment", "multiple departments",
        "nobody helped", "still unresolved"
    ]

    if any(term in text for term in high_risk_terms):
        return "Complex Issues"

    keywords = {
        "IT": [
            "computer", "laptop", "software", "wifi", "wi-fi",
            "internet", "printer", "login", "password", "email",
            "system error", "technical", "account access"
        ],
        "Admin": [
            "id card", "identity card", "office", "desk",
            "chair", "facility", "facilities", "housekeeping",
            "maintenance", "office access", "equipment"
        ],
        "HR": [
            "leave", "attendance", "holiday", "payroll query",
            "onboarding", "resignation", "employee policy",
            "workplace", "hr", "human resources"
        ],
        "Accountant": [
            "salary", "payslip", "pay slip", "reimbursement",
            "invoice", "expense claim", "accounts", "payment",
            "bill", "tax deduction"
        ],
    }

    matches = [
        department
        for department, terms in keywords.items()
        if any(term in text for term in terms)
    ]

    # Unclear or cross-department requests go to human-review support.
    if len(matches) != 1:
        return "Complex Issues"

    return matches[0]


def parse_agent_response(content: str) -> dict:
    """Parse the response JSON and provide a safe fallback."""
    content = content.strip()

    if content.startswith("```"):
        lines = content.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        content = "\n".join(lines).strip()

    try:
        data = json.loads(content)
        if not isinstance(data, dict):
            raise ValueError("Expected a JSON object.")

        data["response"] = str(data.get("response", "")).strip()
        data["confidence"] = float(data.get("confidence", 0.5))
        data["confidence"] = max(0.0, min(1.0, data["confidence"]))
        data["escalation_recommended"] = bool(
            data.get("escalation_recommended", False)
        )
        data["escalation_reason"] = str(
            data.get("escalation_reason", "")
        )

        if not data["response"]:
            raise ValueError("The response was empty.")

        return data

    except (json.JSONDecodeError, TypeError, ValueError):
        return {
            "response": (
                "Your request has been received. A support representative "
                "should review it because a reliable answer could not "
                "be generated automatically."
            ),
            "confidence": 0.0,
            "escalation_recommended": True,
            "escalation_reason": "Invalid or incomplete agent response.",
        }


async def process_customer_ticket(
    complaint: str,
    customer_name: str = "",
    order_id: str = "",
    selected_department: str = "",
) -> dict:
    """Route a ticket to one of five AutoGen department agents."""

    if not complaint or not complaint.strip():
        raise ValueError("Please enter a customer complaint.")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing from your .env file.")

    department = (
    selected_department
    if selected_department in DEPARTMENTS
    else route_department(complaint)
    )

    urgency = (
        "High"
        if any(
            word in complaint.lower()
            for word in [
                "urgent", "emergency", "fraud", "breach",
                "locked out", "cannot work", "can't work",
                "legal", "harassment"
            ]
        )
        else "Medium"
    )

    query_analysis = {
        "category": department,
        "urgency": urgency,
        "sentiment": (
            "Frustrated"
            if any(
                word in complaint.lower()
                for word in [
                    "angry", "frustrated", "unacceptable",
                    "terrible", "again", "nobody helped"
                ]
            )
            else "Neutral"
        ),
        "summary": complaint.strip()[:250],
    }

    # Search existing company documents for relevant information.
    knowledge_result = search_kb(complaint, category=department)

    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        api_key=api_key,
    )

    agents = {
        name: AssistantAgent(
            name=name.lower().replace(" ", "_") + "_agent",
            model_client=model_client,
            system_message=(
                instructions
                + """
Respond helpfully and professionally.
Use the supplied company-document passages when relevant.
Do not invent company policies, approvals, or completed actions.
If company-specific information is missing, say so and recommend
human review instead of guessing.

Return ONLY a valid JSON object with these keys:
response, confidence, escalation_recommended, escalation_reason.

confidence must be a number from 0 to 1.
escalation_recommended must be true or false.
"""
            ),
        )
        for name, instructions in DEPARTMENTS.items()
    }

    try:
        agent = agents[department]

        task = {
            "department": department,
            "customer_name": customer_name or "Not provided",
            "order_id": order_id or "Not provided",
            "complaint": complaint,
            "knowledge_base": knowledge_result,
        }

        result = await agent.run(
            task=(
                "Handle this support request using the supplied information. "
                "Return the required JSON only.\n"
                + json.dumps(task, ensure_ascii=False)
            )
        )

        content = result.messages[-1].content
        if not isinstance(content, str):
            content = ""

        resolution = parse_agent_response(content)

        # Missing company information or high-risk requests require review.
        if (
            urgency == "High"
            or not knowledge_result.get("found", False)
            or resolution["confidence"] < 0.6
            or department == "Complex Issues"
        ):
            resolution["escalation_recommended"] = True

            if not resolution["escalation_reason"]:
                resolution["escalation_reason"] = (
                    "Human review is recommended for this request."
                )

        ticket = log_ticket(
            complaint=complaint,
            query_analysis=query_analysis,
            knowledge_result=knowledge_result,
            resolution=resolution,
            customer_name=customer_name,
            order_id=order_id,
        )

        return {
            "query_analysis": query_analysis,
            "knowledge_result": knowledge_result,
            "resolution": resolution,
            "ticket": ticket,
        }

    finally:
        await model_client.close()

