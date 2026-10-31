
import json
from agents.knowledge_agent import search_kb


def main():
    complaint = "My order has not arrived and is delayed."

    result = search_kb(complaint, category="Shipping")

    print(json.dumps(result, indent=4))

    assert result["found"], "Expected a shipping policy match."
    assert "shipping_policy.md" in result["sources"]

    print("\nKnowledge Agent test passed!")


if __name__ == "__main__":
    main()
