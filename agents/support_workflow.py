
from agents.query_agent import analyze_customer_query
from agents.knowledge_agent import search_kb
from agents.resolution_agent import generate_resolution
from agents.log_agent import log_ticket


async def process_customer_ticket(
    complaint: str,
    customer_name: str = "",
    order_id: str = "",
) -> dict:
    """Run a customer ticket through all four support agents."""

    if not complaint or not complaint.strip():
        raise ValueError("Please enter a customer complaint.")

    # Agent 1: Understand and classify the complaint.
    query_analysis = await analyze_customer_query(complaint)

    # Agent 2: Retrieve relevant company-policy passages.
    knowledge_result = search_kb(
        complaint,
        category=query_analysis.get("category", ""),
    )

    # Agent 3: Draft a response based on retrieved passages.
    resolution = await generate_resolution(
        complaint=complaint,
        query_analysis=query_analysis,
        knowledge_result=knowledge_result,
    )

    # Agent 4: Record the ticket and determine its final status.
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
