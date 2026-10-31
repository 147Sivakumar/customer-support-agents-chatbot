
import json
import os

from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import (
    MaxMessageTermination,
    TextMentionTermination,
)
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient

from agents.knowledge_agent import search_kb
from agents.log_agent import log_ticket

load_dotenv()


def search_kb_tool(query: str, category: str = "") -> str:
    """Search company policy documents and return matching passages."""
    return json.dumps(
        search_kb(query, category),
        ensure_ascii=False,
    )


def log_ticket_tool(
    complaint: str,
    query_analysis_json: str,
    knowledge_result_json: str,
    resolution_json: str,
    customer_name: str = "",
    order_id: str = "",
) -> str:
    """Save the completed support ticket and return a LOGGED marker."""
    query_analysis = json.loads(query_analysis_json)
    knowledge_result = json.loads(knowledge_result_json)
    resolution = json.loads(resolution_json)

    ticket = log_ticket(
        complaint=complaint,
        query_analysis=query_analysis,
        knowledge_result=knowledge_result,
        resolution=resolution,
        customer_name=customer_name,
        order_id=order_id,
    )

    return "LOGGED " + json.dumps(ticket, ensure_ascii=False)


async def run_autogen_team(
    complaint: str,
    customer_name: str = "",
    order_id: str = "",
):
    """Run the four AutoGen agents in a fixed round-robin sequence."""

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing from your .env file.")

    model_client = OpenAIChatCompletionClient(
        model="gpt-4o-mini",
        api_key=api_key,
    )

    query_agent = AssistantAgent(
        name="customer_query_agent",
        description="Classifies the complaint and identifies urgency.",
        model_client=model_client,
        system_message="""
Analyze the customer's complaint.
Return one JSON object with category, urgency, sentiment, and summary.
Urgency must be Low, Medium, or High.
Sentiment must be Positive, Neutral, Frustrated, or Angry.
Do not claim the issue is resolved.
""",
    )

    knowledge_agent = AssistantAgent(
        name="knowledge_base_agent",
        description="Retrieves evidence from company policy documents.",
        model_client=model_client,
        tools=[search_kb_tool],
        system_message="""
Use the search_kb_tool to search the company documents.
Use the original customer complaint and the Query Agent's category.
Return the tool's retrieved passages and source filenames.
Do not invent policy information.
""",
    )

    resolution_agent = AssistantAgent(
        name="resolution_agent",
        description="Writes a policy-grounded customer response.",
        model_client=model_client,
        system_message="""
Use the original complaint and the Knowledge Agent's retrieved passages.
Return only JSON with keys response, confidence,
escalation_recommended, and escalation_reason.
Confidence must be between 0 and 1.
Do not invent facts or policies.
If no relevant passage was found, say human review is needed.
Recommend escalation for high urgency, an angry customer, missing
knowledge, legal threats, suspected fraud, payment disputes, or low confidence.
""",
    )

    log_agent = AssistantAgent(
        name="log_agent",
        description="Records the ticket and decides final escalation status.",
        model_client=model_client,
        tools=[log_ticket_tool],
        system_message="""
You must finish the workflow by calling log_ticket_tool exactly once.
Use the original complaint, customer name, and order ID from the first message.
Copy the Query Agent JSON into query_analysis_json.
Copy the Knowledge Agent's retrieved JSON into knowledge_result_json.
Copy the Resolution Agent JSON into resolution_json.
Do not invent values. The tool returns a ticket ID and the word LOGGED.
After the tool succeeds, repeat the LOGGED result and stop.
""",
    )

    team = RoundRobinGroupChat(
        participants=[
            query_agent,
            knowledge_agent,
            resolution_agent,
            log_agent,
        ],
        termination_condition=(
            TextMentionTermination("LOGGED")
            | MaxMessageTermination(12)
        ),
    )

    task = (
        "Process this customer support ticket through all four agents.\n"
        f"Customer complaint: {complaint}\n"
        f"Customer name: {customer_name or 'Not provided'}\n"
        f"Order ID: {order_id or 'Not provided'}\n"
        "Follow the agent order and log the final ticket."
    )

    try:
        return await team.run(task=task)
    finally:
        await model_client.close()
