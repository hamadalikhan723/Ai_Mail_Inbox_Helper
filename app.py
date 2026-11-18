
import os
import streamlit as st
import pandas as pd

from google import genai
from ai_engine import load_company_knowledge, generate_reply


st.set_page_config(
    page_title="MUST AI Inbox Helper",
    page_icon="📩",
    layout="wide"
)

st.title("📩 MUST AI Inbox Helper")
st.caption("AI-assisted candidate message classification and reply drafting")

# API key
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")

st.write("Secrets file detected:", "GEMINI_API_KEY" in st.secrets)
st.write("Environment key detected:", bool(os.getenv("GEMINI_API_KEY")))

if not api_key:
    st.error("Gemini API key not found. Configure GEMINI_API_KEY in Streamlit secrets.")
    st.stop()

client = genai.Client(api_key=api_key)

# Load company information
company_data = load_company_knowledge()
company_context = str(company_data)

st.info(
    "This tool drafts replies for HR review. "
    "It does not send emails or make hiring decisions."
)

st.subheader("1. Add candidate messages")

input_method = st.radio(
    "Choose input method:",
    ["Paste messages", "Upload CSV"],
    horizontal=True
)

messages = []

if input_method == "Paste messages":
    st.write("For multiple messages, separate each message with a line containing: `---EMAIL---`")

    pasted_text = st.text_area(
        "Paste candidate messages",
        height=220,
        placeholder="Paste one or more candidate messages here..."
    )

    if pasted_text.strip():
        messages = [
            msg.strip()
            for msg in pasted_text.split("---EMAIL---")
            if msg.strip()
        ]

else:
    uploaded_file = st.file_uploader(
        "Upload candidate messages CSV",
        type=["csv"]
    )

    if uploaded_file:
        input_df = pd.read_csv(uploaded_file)

        if "message" not in input_df.columns:
            st.error("CSV must contain a 'message' column.")
            st.stop()

        for index, row in input_df.iterrows():
            messages.append({
                "name": row.get("candidate_name", f"Candidate {index + 1}"),
                "message": str(row["message"])
            })

if st.button("Generate Reply Drafts", type="primary"):
    if not messages:
        st.warning("Please add at least one candidate message.")
    else:
        results = []

        progress = st.progress(0)
        status = st.empty()

        for index, item in enumerate(messages):
            if isinstance(item, dict):
                candidate_name = str(item["name"])
                message = item["message"]
            else:
                candidate_name = f"Candidate {index + 1}"
                message = item

            status.write(
                f"Processing {index + 1} of {len(messages)}: {candidate_name}"
            )

            try:
                result = generate_reply(
                    client,
                    message,
                    company_context
                )

                results.append({
                    "candidate_name": candidate_name,
                    "original_message": message,
                    "category": result["category"],
                    "review_status": result["review_status"],
                    "review_reason": result["review_reason"],
                    "reply_draft": result["reply_draft"],
                    "hr_decision": "Pending"
                })

            except Exception as error:
                results.append({
                    "candidate_name": candidate_name,
                    "original_message": message,
                    "category": "Processing Error",
                    "review_status": "Needs HR Verification",
                    "review_reason": str(error),
                    "reply_draft": "Please review this message manually.",
                    "hr_decision": "Pending"
                })

            progress.progress((index + 1) / len(messages))

        st.session_state["results"] = results
        status.success("Draft generation completed!")

# Display results
if "results" in st.session_state:
    st.divider()
    st.subheader("2. Review generated replies")

    results = st.session_state["results"]

    for index, item in enumerate(results):
        with st.expander(
            f"{index + 1}. {item['candidate_name']} — {item['category']}",
            expanded=False
        ):
            st.markdown("**AI review status**")
            st.write(item["review_status"])

            st.markdown("**Review reason**")
            st.write(item["review_reason"])

            edited_draft = st.text_area(
                "Reply draft — HR can edit this",
                value=item["reply_draft"],
                key=f"draft_{index}"
            )

            decision = st.selectbox(
                "HR review decision",
                ["Pending", "Approved", "Rejected"],
                index=["Pending", "Approved", "Rejected"].index(
                    item["hr_decision"]
                ),
                key=f"decision_{index}"
            )

            results[index]["reply_draft"] = edited_draft
            results[index]["hr_decision"] = decision

    st.divider()

    approved = [
        item for item in results
        if item["hr_decision"] == "Approved"
    ]

    st.write(
        f"**Total messages:** {len(results)}  |  "
        f"**Approved drafts:** {len(approved)}  |  "
        f"**Pending / rejected:** {len(results) - len(approved)}"
    )

    if approved:
        approved_df = pd.DataFrame(approved)

        csv_data = approved_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "Download HR-approved drafts",
            data=csv_data,
            file_name="approved_reply_drafts.csv",
            mime="text/csv"
        )

    all_df = pd.DataFrame(results)

    st.download_button(
        "Download all results",
        data=all_df.to_csv(index=False).encode("utf-8"),
        file_name="all_candidate_drafts.csv",
        mime="text/csv"
    )

    st.caption(
        "Approved means reviewed by HR only. "
        "Messages are never sent automatically."
    )
