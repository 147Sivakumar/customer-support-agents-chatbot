
import asyncio
import json

from agents.support_workflow import process_customer_ticket


async def main():
    result = await process_customer_ticket(
        complaint=(
            "My order was supposed to arrive yesterday, "
            "but it has not arrived. Please help."
        ),
        customer_name="Workflow Test",
        order_id="ORD-2001",
    )

    print("\nComplete Support Workflow Result:")
    print(json.dumps(result, indent=4, ensure_ascii=False))

    assert result["query_analysis"]
    assert result["knowledge_result"]
    assert result["resolution"]["response"]
    assert result["ticket"]["ticket_id"]
    assert result["ticket"]["status"] in {"Resolved", "Escalated"}

    print("\nComplete support workflow test passed!")


if __name__ == "__main__":
    asyncio.run(main())
