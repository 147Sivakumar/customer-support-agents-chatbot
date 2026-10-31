
import asyncio

import pandas as pd
import streamlit as st

from agents.support_workflow import process_customer_ticket
from agents.log_agent import LOG_FILE


st.set_page_config(
    page_title="AI Customer Support Automation",
    page_icon="🎧",
    layout="wide",
)

st.title("🎧 AI Customer Support Automation")
st.write(
    "Four AI agents work together to classify complaints, "
    "retrieve company policies, draft responses, and log tickets."
)


def load_tickets():
    """Load the ticket history safely."""
    if not LOG_FILE.exists() or LOG_FILE.stat().st_size == 0:
        return pd.DataFrame()

    try:
        return pd.read_csv(LOG_FILE, encoding="utf-8-sig")
    except (OSError, pd.errors.EmptyDataError):
        return pd.DataFrame()


with st.form("customer_complaint_form"):
    st.subheader("Submit a customer complaint")

    customer_name = st.text_input(
        "Customer name (optional)",
        placeholder="e.g. Alex",
    )

    order_id = st.text_input(
        "Order ID (optional)",
        placeholder="e.g. ORD-1001",
    )

    complaint = st.text_area(
        "Describe the customer's issue",
        placeholder="Enter the customer complaint here...",
        height=150,
    )

    submitted = st.form_submit_button(
        "Process Complaint",
        type="primary",
    )


if submitted:
    if not complaint.strip():
        st.error("Please enter a customer complaint.")
    else:
        try:
            with st.spinner("The four agents are processing the ticket..."):
                result = asyncio.run(
                    process_customer_ticket(
                        complaint=complaint,
                        customer_name=customer_name,
                        order_id=order_id,
                    )
                )

            query = result["query_analysis"]
            knowledge = result["knowledge_result"]
            resolution = result["resolution"]
            ticket = result["ticket"]

            st.session_state["latest_result"] = result

            st.success(
                f"Ticket created successfully: {ticket['ticket_id']}"
            )

        except Exception as exc:
            st.error(
                "The ticket could not be processed. "
                "Check your API configuration and terminal for details."
            )
            st.exception(exc)


if "latest_result" in st.session_state:
    result = st.session_state["latest_result"]

    query = result["query_analysis"]
    knowledge = result["knowledge_result"]
    resolution = result["resolution"]
    ticket = result["ticket"]

    st.divider()
    st.header("Agent Results")

    with st.expander("1. Customer Query Agent", expanded=True):
        st.write("**Category:**", query.get("category", "Other"))
        st.write("**Urgency:**", query.get("urgency", "Medium"))
        st.write("**Sentiment:**", query.get("sentiment", "Neutral"))
        st.write("**Summary:**", query.get("summary", ""))

    with st.expander("2. Knowledge Base Agent", expanded=True):
        if knowledge.get("found"):
            st.write("**Source documents:**")
            for source in knowledge.get("sources", []):
                st.write(f"- `{source}`")

            for index, passage in enumerate(
                knowledge.get("passages", []), start=1
            ):
                st.markdown(
                    f"**Passage {index} — {passage['source']}**"
                )
                st.write(passage["passage"])
        else:
            st.warning(
                "No matching company policy was found. "
                "Human support review is required."
            )

    with st.expander("3. Resolution Agent", expanded=True):
        st.write("**Drafted customer response:**")
        st.info(resolution.get("response", ""))

        st.write(
            "**Confidence:**",
            f"{float(resolution.get('confidence', 0)):.0%}",
        )

        st.write(
            "**Escalation recommended:**",
            "Yes" if resolution.get("escalation_recommended") else "No",
        )

        if resolution.get("escalation_reason"):
            st.write(
                "**Reason:**",
                resolution["escalation_reason"],
            )

    with st.expander("4. Log Agent", expanded=True):
        if ticket["status"] == "Escalated":
            st.error("Status: Escalated")
        else:
            st.success("Status: Resolved")

        st.write("**Ticket ID:**", ticket["ticket_id"])
        st.write("**Timestamp:**", ticket["timestamp"])

        if ticket["escalation_reason"]:
            st.write(
                "**Escalation reason:**",
                ticket["escalation_reason"],
            )


st.divider()
st.header("Ticket Log History")

tickets_df = load_tickets()

if not tickets_df.empty:
    st.dataframe(
        tickets_df,
        use_container_width=True,
        hide_index=True,
    )

    csv_data = tickets_df.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        label="Download Ticket Log as CSV",
        data=csv_data,
        file_name="customer_support_tickets.csv",
        mime="text/csv",
    )
else:
    st.info(
        "No tickets have been logged yet. "
        "Submit a complaint above to create the first ticket."
    )
