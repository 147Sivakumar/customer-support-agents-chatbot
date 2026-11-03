
import asyncio

import pandas as pd
import streamlit as st

from agents.support_workflow import process_customer_ticket
from agents.log_agent import LOG_FILE

st.set_page_config(
    page_title="Support Desk Dashboard",
    page_icon="🎧",
    layout="wide",
)

# Simple dashboard styling
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 2rem;
    }
    div[data-testid="stMetric"] {
        border: 1px solid #e5e7eb;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

DEPARTMENTS = [
    "Auto-detect department",
    "IT",
    "Admin",
    "HR",
    "Accountant",
    "Complex Issues",
]

st.title("🎧 Support Desk Dashboard")
st.caption("Submit a request, choose a department, and track support tickets.")

# Read ticket history
def load_tickets():
    if LOG_FILE.exists():
        try:
            return pd.read_csv(LOG_FILE).fillna("")
        except (pd.errors.EmptyDataError, pd.errors.ParserError):
            return pd.DataFrame()
    return pd.DataFrame()


tickets = load_tickets()

# Dashboard summary
total_tickets = len(tickets)
open_tickets = 0
escalated_tickets = 0
resolved_tickets = 0

if not tickets.empty and "status" in tickets.columns:
    statuses = tickets["status"].astype(str).str.lower()
    escalated_tickets = int(statuses.str.contains("escalat").sum())
    resolved_tickets = int(statuses.str.contains("resolv|clos", regex=True).sum())
    open_tickets = total_tickets - escalated_tickets - resolved_tickets

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Tickets", total_tickets)
m2.metric("Open / Other", max(open_tickets, 0))
m3.metric("Escalated", escalated_tickets)
m4.metric("Resolved / Closed", resolved_tickets)

st.divider()

left, right = st.columns([1, 1.5], gap="large")

with left:
    st.subheader("📝 Submit a Support Request")

    with st.form("support_form", clear_on_submit=False):
        customer_name = st.text_input("Customer / Employee Name")
        order_id = st.text_input("Ticket Reference (optional)")

        department_choice = st.selectbox(
            "Choose Department",
            DEPARTMENTS,
        )

        complaint = st.text_area(
            "Describe your issue",
            placeholder=(
                "Example: My laptop cannot connect to the office Wi-Fi."
            ),
            height=150,
        )

        submitted = st.form_submit_button(
            "Submit Request",
            type="primary",
            use_container_width=True,
        )

    if submitted:
        if not complaint.strip():
            st.warning("Please describe your issue first.")
        else:
            selected_department = (
                ""
                if department_choice == "Auto-detect department"
                else department_choice
            )

            try:
                with st.spinner("Processing your support request..."):
                    result = asyncio.run(
                        process_customer_ticket(
                            complaint=complaint.strip(),
                            customer_name=customer_name.strip(),
                            order_id=order_id.strip(),
                            selected_department=selected_department,
                        )
                    )

                st.session_state["latest_result"] = result
                st.success("Support request processed successfully.")

            except Exception as exc:
                st.error("The request could not be processed.")
                st.caption(str(exc))

with right:
    st.subheader("📌 Latest Ticket Result")

    result = st.session_state.get("latest_result")

    if result:
        analysis = result.get("query_analysis", {})
        resolution = result.get("resolution", {})
        ticket = result.get("ticket", {})

        st.write(
            "**Department:**",
            analysis.get("category", "Not available"),
        )
        st.write(
            "**Urgency:**",
            analysis.get("urgency", "Not available"),
        )
        st.write(
            "**Sentiment:**",
            analysis.get("sentiment", "Not available"),
        )

        st.markdown("**Suggested Response**")
        st.write(
            resolution.get(
                "response",
                "No response was generated.",
            )
        )

        if ticket:
            st.write(
                "**Ticket ID:**",
                ticket.get("ticket_id", ticket.get("id", "See ticket history")),
            )
            st.write(
                "**Status:**",
                ticket.get("status", "See ticket history"),
            )

        if resolution.get("escalation_recommended", False):
            st.warning(
                resolution.get(
                    "escalation_reason",
                    "Human review is recommended.",
                )
            )
        else:
            st.info("No escalation was recommended by the agent.")

        with st.expander("View knowledge-base result"):
            st.json(result.get("knowledge_result", {}))

    else:
        st.info(
            "Your latest ticket result will appear here after you submit a request."
        )

st.divider()

# Ticket history
st.subheader("📋 Ticket History")

tickets = load_tickets()

if tickets.empty:
    st.info("No ticket records found. Submit a request to create a new record.")
else:
    st.dataframe(
        tickets,
        use_container_width=True,
        hide_index=True,
    )

    csv_data = tickets.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Ticket History (CSV)",
        data=csv_data,
        file_name="support_tickets.csv",
        mime="text/csv",
    )

st.divider()

# Clear old records only after explicit confirmation
with st.expander("⚙️ Manage Ticket Records"):
    st.warning(
        "Clearing history permanently removes the saved ticket log. "
        "It does not delete your agents, code, or knowledge-base files."
    )

    confirm_clear = st.checkbox(
        "I confirm that I want to clear all saved ticket records."
    )

    if st.button("Clear Ticket History", type="secondary"):
        if not confirm_clear:
            st.warning("Tick the confirmation box before clearing history.")
        else:
            try:
                if LOG_FILE.exists():
                    LOG_FILE.unlink()

                st.session_state.pop("latest_result", None)
                st.success("Old ticket history cleared.")
                st.rerun()

            except OSError as exc:
                st.error(f"Could not clear ticket history: {exc}")
