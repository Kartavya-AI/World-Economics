import streamlit as st
import os
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from src.world_economics.crew import WorldEconomicsCrew
import traceback

# Page config
st.set_page_config(
    page_title="🌍 World Economics AI",
    layout="centered",
    page_icon="📊"
)
with st.sidebar:
    st.header("⚙️ AI & API Settings")

    # Gemini API Key
    gemini_api_key = st.text_input(
        "Gemini API Key",
        type="password",
        value=st.session_state.get("GEMINI_API_KEY", ""),
        help="Enter your Gemini (Google AI) API key"
    )

    # Serper API Key
    serper_api_key = st.text_input(
        "Serper API Key",
        type="password",
        value=st.session_state.get("SERPER_API_KEY", ""),
        help="Enter your Serper (Google Search) API key"
    )

    # AI Model selection
    model_choice = st.selectbox(
        "Select AI Model",
        ["gemini/gemini-2.5-flash-preview-05-20", "", "gemini-pro", "mistral-medium"],
        index=["gemini/gemini-2.5-flash-preview-05-20", "", "gemini-pro", "mistral-medium"].index(
            st.session_state.get("MODEL_CHOICE", "gemini/gemini-2.5-flash-preview-05-20")
        ),
        help="Choose which AI model to use"
    )

    # Save Button
    if st.button("💾 Save Settings"):
        updated = False

        if gemini_api_key:
            st.session_state["GEMINI_API_KEY"] = gemini_api_key
            os.environ["GEMINI_API_KEY"] = gemini_api_key
            updated = True

        if serper_api_key:
            st.session_state["SERPER_API_KEY"] = serper_api_key
            os.environ["SERPER_API_KEY"] = serper_api_key
            updated = True

        if model_choice:
            st.session_state["MODEL"] = model_choice
            os.environ["MODEL"] = model_choice
            updated = True

        if updated:
            st.success("✅ Settings saved successfully!")
        else:
            st.error("❌ Please enter at least one API key or model selection.")

from src.world_economics.tools.serper_tool import serper_tool
st.title("🌍 World Economics AI")
st.markdown("Get structured economic insights and interact with a live economic assistant.")

FINAL_REPORT_PATH = "final_report.md"

# Helper function
def load_final_report():
    if os.path.exists(FINAL_REPORT_PATH):
        with open(FINAL_REPORT_PATH, "r") as f:
            return f.read()
    return None

# Tabs for cleaner UI
tabs = st.tabs(["📘 Report Generator", "💬 Follow-Up Assistant"])

# --- Tab 1: Report Generator ---
with tabs[0]:
    st.subheader("🧠 Generate Economic Report")
    user_query = st.text_area("Enter your economic question", placeholder="e.g. How does the Fed’s interest rate policy affect developing economies?")
    submit = st.button("📊 Generate Report")

    if submit:
        if not user_query.strip():
            st.warning("⚠️ Please enter a valid economic question.")
        else:
            st.info("⏳ Generating report. Please wait...")
            try:
                inputs = {
                    "user_query": user_query,
                    "current_year": str(datetime.now().year)
                }
                WorldEconomicsCrew().crew().kickoff(inputs=inputs)
                st.success("✅ Report generated successfully!")
            except Exception as e:
                st.error(f"❌ Error generating report: {e}")
                st.code(traceback.format_exc())

    # Show Report if available
    final_report = load_final_report()
    if final_report:
        st.markdown("### 📄 Final Economic Report")
        st.markdown(final_report, unsafe_allow_html=True)

        with open(FINAL_REPORT_PATH, "r") as f:
            st.download_button("📥 Download Report", f, file_name="world_economics_report.md", mime="text/markdown")

# --- Tab 2: Chat Assistant ---
with tabs[1]:
    st.subheader("💬 Ask Follow-up Questions")

    final_report = load_final_report()

    if not final_report:
        st.info("📘 Please generate a report first in the 'Report Generator' tab.")
    else:
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        follow_up = st.chat_input("Ask a follow-up question based on the report...")

        if follow_up:
            with st.spinner("🤖 Thinking..."):
                try:
                    # Define inline agent
                    chat_agent = Agent(
                        role="Economic Report Assistant",
                        goal="Answer follow-up questions based on the economic report provided.",
                        backstory="You are a helpful assistant trained to analyze economic reports and respond to user queries with clarity and accuracy.",
                        tools=[serper_tool],
                        verbose=True
                    )

                    # Define task using context
                    chat_task = Task(
                        description=f"""Based on the report:

{final_report}

Answer the user's question:

{follow_up}
try answer within context if not possible find thorugh search tool.""",
                        expected_output="A clear, concise and informative response to the user's question.",
                        agent=chat_agent
                    )

                    # Run the crew
                    chat_crew = Crew(
                        agents=[chat_agent],
                        tasks=[chat_task],
                        process=Process.sequential
                    )
                    response = chat_crew.kickoff()

                    # Append chat history
                    st.session_state.chat_history.append(("user", follow_up))
                    st.session_state.chat_history.append(("assistant", response))

                except Exception as e:
                    st.error(f"❌ Error processing follow-up: {e}")
                    st.code(traceback.format_exc())

        # Show chat history
        for role, msg in st.session_state.chat_history:
            with st.chat_message(role):
                st.markdown(msg)
