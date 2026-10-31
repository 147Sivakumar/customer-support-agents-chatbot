
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"

STOP_WORDS = {
    "the", "and", "for", "are", "was", "were", "has", "have",
    "had", "not", "but", "with", "from", "that", "this", "you",
    "your", "our", "they", "their", "them", "can", "could",
    "would", "should", "please", "help", "need", "want", "into",
    "about", "when", "what", "where", "how", "its", "still",
    "my", "me", "i", "it", "is", "to", "of", "in", "on", "by",
    "a", "an", "be", "do", "does", "did", "as", "at", "or",
}

CATEGORY_TERMS = {
    "Shipping": {
        "shipping", "shipment", "delivery", "delayed", "arrived",
        "arrival", "tracking", "dispatch", "missing", "package",
        "parcel", "order",
    },
    "Refund": {
        "refund", "return", "returned", "eligibility", "eligible",
        "payment", "damaged", "replacement",
    },
    "Account": {
        "account", "login", "password", "sign", "access",
        "email", "security", "fraud", "suspicious",
    },
    "Product": {
        "product", "defective", "damaged", "gift", "card",
        "features", "specs", "warranty",
    },
    "Billing": {
        "billing", "payment", "charged", "chargeback",
        "unauthorized", "invoice",
    },
}


def tokenize(text: str) -> set[str]:
    """Extract meaningful words from text."""
    words = set(re.findall(r"[a-z0-9]+", text.lower()))
    return {
        word for word in words
        if len(word) > 2 and word not in STOP_WORDS
    }


def search_kb(query: str, category: str = "") -> dict:
    """Search Markdown documents and rank relevant policy passages."""

    if not query or not query.strip():
        return {
            "found": False,
            "passages": [],
            "sources": [],
            "message": "The search query is empty.",
        }

    if not KNOWLEDGE_BASE_DIR.exists():
        raise FileNotFoundError(
            f"Knowledge base directory not found: {KNOWLEDGE_BASE_DIR}"
        )

    query_words = tokenize(query)
    category_words = CATEGORY_TERMS.get(category, set())
    results = []

    for file_path in sorted(KNOWLEDGE_BASE_DIR.glob("*.md")):
        content = file_path.read_text(encoding="utf-8")
        sections = re.split(r"(?m)^##\s+", content)

        for section in sections:
            passage = section.strip()
            if not passage:
                continue

            passage_words = tokenize(passage)
            if not passage_words:
                continue

            overlap = query_words & passage_words

            # Count matches, but give extra weight to category-specific terms.
            score = len(overlap)
            score += 2 * len(overlap & category_words)

            # A matching section heading is useful evidence of relevance.
            heading = passage.splitlines()[0].strip("# ").lower()
            heading_words = tokenize(heading)
            score += 2 * len(query_words & heading_words)

            if score > 0:
                results.append({
                    "source": file_path.name,
                    "passage": passage,
                    "score": score,
                })

    results.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    # Keep only the strongest matches, up to five passages.
    matches = results[:5]

    return {
        "found": bool(matches),
        "passages": [
            {
                "source": item["source"],
                "passage": item["passage"],
            }
            for item in matches
        ],
        "sources": list(dict.fromkeys(
            item["source"] for item in matches
        )),
        "message": (
            "Matching company documents found."
            if matches
            else "No matching company document was found."
        ),
    }
