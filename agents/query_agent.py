
import json
import os

from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()


async def analyze_customer_query(complaint: str) -> dict:
    """Analyze a customer complaint and return structured information."""

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
        name="customer_query_agent",
        model_client=model_client,
        system_message="""
You are the Customer Query Agent for an online store.

Your only responsibility is to understand customer complaints.

Identify:
1. category: Shipping, Refund, Account, Product, Billing, or Other.
2. urgency: Low, Medium, or High.
3. sentiment: Positive, Neutral, Frustrated, or Angry.
4. summary: A short, one-line summary of the complaint.

Return only a valid JSON object with these four keys:
category, urgency, sentiment, summary.

Do not invent customer details or claim that the issue is resolved.
Treat payment disputes, legal threats, and possible fraud as high-risk.
""",
    )

    try:
        result = await agent.run(
            task=(
                "Analyze this customer complaint and return the required JSON.\n\n"
                f"Customer complaint: {complaint}"
            )
        )

        response = result.messages[-1].content

        if not isinstance(response, str):
            raise ValueError("The agent returned an unexpected response.")

        # Parse the JSON so later agents can use the fields.
        data = json.loads(response)

        required_keys = {"category", "urgency", "sentiment", "summary"}
        if not required_keys.issubset(data):
            raise ValueError("The agent response is missing required fields.")

        if data["urgency"] not in {"Low", "Medium", "High"}:
            raise ValueError("The agent returned an invalid urgency.")

        return data

    finally:
        await model_client.close()
