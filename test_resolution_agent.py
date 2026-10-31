
import asyncio
import json

from agents.knowledge_agent import search_kb
from agents.query_agent import analyze_customer_query
from agents.resolution_agent import generate_resolution


async def main():
    complaint = (
        "My order was due yesterday and it still has not arrived."
    )

    query_analysis = await analyze_customer_query(complaint)

    knowledge_result = search_kb(
        complaint,
        category=query_analysis["category"],
    )

    resolution = await generate_resolution(
        complaint,
        query_analysis,
        knowledge_result,
    )

    print("\nQuery Analysis:")
    print(json.dumps(query_analysis, indent=4))

    print("\nKnowledge Base Result:")
    print(json.dumps(knowledge_result, indent=4))

    print("\nResolution Agent Result:")
    print(json.dumps(resolution, indent=4))

    assert resolution["response"].strip()
    assert 0 <= resolution["confidence"] <= 1
    assert isinstance(resolution["escalation_recommended"], bool)

    print("\nResolution Agent test passed!")


if __name__ == "__main__":
    asyncio.run(main())
