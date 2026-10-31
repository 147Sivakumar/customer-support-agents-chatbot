
import asyncio
import json

from agents.query_agent import analyze_customer_query


async def main():
    complaint = "My order was due yesterday and it still has not arrived."

    result = await analyze_customer_query(complaint)

    print("\nCustomer Query Agent Result:")
    print(json.dumps(result, indent=4))


if __name__ == "__main__":
    asyncio.run(main())
