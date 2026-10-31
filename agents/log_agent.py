
import csv
from datetime import datetime
from pathlib import Path
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOGS_DIR / "tickets.csv"

COLUMNS = [
    "ticket_id",
    "timestamp",
    "customer_name",
    "order_id",
    "complaint",
    "category",
    "urgency",
    "sentiment",
    "kb_sources",
    "response",
    "status",
    "escalation_reason",
]


def log_ticket(
    complaint: str,
    query_analysis: dict,
    knowledge_result: dict,
    resolution: dict,
    customer_name: str = "",
    order_id: str = "",
) -> dict:
    """Determine ticket status and append the ticket to a CSV file."""

    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    urgency = query_analysis.get("urgency", "Medium")
    sentiment = query_analysis.get("sentiment", "Neutral")
    confidence = float(resolution.get("confidence", 0))

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

    reasons = []

    if urgency == "High":
        reasons.append("High urgency")

    if sentiment == "Angry":
        reasons.append("Customer sentiment is Angry")

    if not knowledge_result.get("found", False):
        reasons.append("No matching knowledge-base document found")

    if confidence < 0.6:
        reasons.append("Low resolution confidence")

    if any(term in complaint_lower for term in risk_terms):
        reasons.append("Potential legal, fraud, or payment risk")

    if resolution.get("escalation_recommended", False):
        agent_reason = resolution.get("escalation_reason", "")
        if agent_reason:
            reasons.append(agent_reason)
        elif not reasons:
            reasons.append("Resolution Agent recommended escalation")

    # Remove duplicate reasons while preserving order.
    reasons = list(dict.fromkeys(reasons))

    status = "Escalated" if reasons else "Resolved"
    escalation_reason = "; ".join(reasons)

    ticket = {
        "ticket_id": f"TKT-{uuid4().hex[:8].upper()}",
        "timestamp": datetime.now().astimezone().isoformat(timespec="seconds"),
        "customer_name": customer_name.strip(),
        "order_id": order_id.strip(),
        "complaint": complaint.strip(),
        "category": query_analysis.get("category", "Other"),
        "urgency": urgency,
        "sentiment": sentiment,
        "kb_sources": "; ".join(knowledge_result.get("sources", [])),
        "response": resolution.get("response", ""),
        "status": status,
        "escalation_reason": escalation_reason,
    }

    file_exists = LOG_FILE.exists() and LOG_FILE.stat().st_size > 0

    with LOG_FILE.open("a", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=COLUMNS)

        if not file_exists:
            writer.writeheader()

        writer.writerow(ticket)

    return ticket
