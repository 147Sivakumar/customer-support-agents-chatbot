
import asyncio

from team import run_autogen_team


async def main():
    result = await run_autogen_team(
        complaint=(
            "My order was supposed to arrive yesterday, "
            "but it has not arrived."
        ),
        customer_name="AutoGen Team Test",
        order_id="ORD-TEAM-001",
    )

    for message in result.messages:
        print(f"\n--- {message.source} ---")
        print(message.content)

    logged = any(
        isinstance(message.content, str)
        and "LOGGED" in message.content
        for message in result.messages
    )

    if not logged:
        raise RuntimeError(
            "The team did not produce a LOGGED marker. "
            "Check the final messages above."
        )

    print("\nAutoGen team test passed!")


if __name__ == "__main__":
    asyncio.run(main())
