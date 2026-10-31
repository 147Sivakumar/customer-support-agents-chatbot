
import json

from agents.log_agent import log_ticket


def main():
    complaint = "My order was due yesterday and it still has not arrived."

    query_analysis = {
        "category": "Shipping",
        "urgency": "High",
        "sentiment": "Frustrated",
        "summary": "The order is overdue.",
    }

    knowledge_result = {
        "found": True,
        "sources": ["shipping_policy.md"],
    }

    resolution = {
        "response": (
            "Please check your tracking number. "
            "If the delay cannot be resolved, human support will review it."
        ),
        "confidence": 0.9,
        "escalation_recommended": True,
        "escalation_reason": "High urgency regarding a delayed order.",
    }

    ticket = log_ticket(
        complaint=complaint,
        query_analysis=query_analysis,
        knowledge_result=knowledge_result,
        resolution=resolution,
        customer_name="Test Customer",
        order_id="ORD-1001",
    )

    print("\nLogged Ticket:")
    print(json.dumps(ticket, indent=4))

    print("\nCSV file location:")
    print(ticket["ticket_id"])
    print("logs\\tickets.csv")

    assert ticket["status"] == "Escalated"
    assert ticket["ticket_id"].startswith("TKT-")
    assert ticket["escalation_reason"]
    print("\nLog Agent test passed!")


if __name__ == "__main__":
    main()
