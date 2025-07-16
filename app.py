import streamlit as st
import os
from datetime import datetime
from crewai import Agent, Task, Crew, Process
from src.world_economics.crew import WorldEconomicsCrew
import traceback

# Page config
st.set_page_config(
    page_title="🌍 World Economics AI",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .main-header h1 {
        color: white !important;
        font-size: 2.8rem;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 0;
    }
    
    .sidebar-header {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        text-align: center;
        color: white;
    }
    
    .sidebar-header h2 {
        color: white !important;
        margin-bottom: 0.5rem;
        font-size: 1.4rem;
    }
    
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border: 1px solid #e9ecef;
        margin-bottom: 1.5rem;
    }
    
    .status-card {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border-left: 4px solid;
    }
    
    .status-success {
        background: #d4edda;
        border-left-color: #28a745;
        color: #155724;
    }
    
    .status-warning {
        background: #fff3cd;
        border-left-color: #ffc107;
        color: #856404;
    }
    
    .status-error {
        background: #f8d7da;
        border-left-color: #dc3545;
        color: #721c24;
    }
    
    .status-info {
        background: #cce7ff;
        border-left-color: #007bff;
        color: #004085;
    }
    
    .metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metric-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #e9ecef;
        transition: transform 0.2s ease;
    }
    
    .metric-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #6c757d;
        font-weight: 500;
    }
    
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 8px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    
    .chat-container {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
    
    .report-container {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        border: 1px solid #e9ecef;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .feature-highlight {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .api-status {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-left: 0.5rem;
    }
    
    .api-connected {
        background: #d4edda;
        color: #155724;
    }
    
    .api-disconnected {
        background: #f8d7da;
        color: #721c24;
    }
    
    .tab-content {
        padding: 1rem 0;
    }
    
    .sidebar-section {
        margin-bottom: 2rem;
        padding: 1rem;
        background: #f8f9fa;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# Enhanced Sidebar
with st.sidebar:
    st.markdown("""
    <div class="sidebar-header">
        <h2>⚙️ AI & API Settings</h2>
        <p>Configure your AI models and API keys</p>
    </div>
    """, unsafe_allow_html=True)

    # API Keys Section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("### 🔑 API Configuration")
    
    # Gemini API Key
    gemini_api_key = st.text_input(
        "Gemini API Key",
        type="password",
        value=st.session_state.get("GEMINI_API_KEY", ""),
        help="Enter your Gemini (Google AI) API key for advanced AI capabilities"
    )
    
    # Show status
    if gemini_api_key:
        st.markdown('<span class="api-status api-connected">✅ Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="api-status api-disconnected">❌ Not Connected</span>', unsafe_allow_html=True)

    # Serper API Key
    serper_api_key = st.text_input(
        "Serper API Key",
        type="password",
        value=st.session_state.get("SERPER_API_KEY", ""),
        help="Enter your Serper (Google Search) API key for real-time data"
    )
    
    # Show status
    if serper_api_key:
        st.markdown('<span class="api-status api-connected">✅ Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="api-status api-disconnected">❌ Not Connected</span>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

    # Model Selection Section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("### 🤖 AI Model Selection")
    
    model_choice = st.selectbox(
        "Select AI Model",
        ["gemini/gemini-2.5-flash-preview-05-20", "gemini-pro", "mistral-medium"],
        index=["gemini/gemini-2.5-flash-preview-05-20", "gemini-pro", "mistral-medium"].index(
            st.session_state.get("MODEL_CHOICE", "gemini/gemini-2.5-flash-preview-05-20")
        ),
        help="Choose which AI model to use for analysis"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)

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

    # Features Section
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("### ✨ Features")
    st.markdown("""
    - 🔍 **Real-time Analysis**: Live economic data
    - 📊 **Comprehensive Reports**: Detailed insights
    - 💬 **Interactive Chat**: Follow-up questions
    - 📈 **Market Trends**: Latest economic indicators
    - 🌐 **Global Perspective**: Worldwide economic view
    """)
    st.markdown('</div>', unsafe_allow_html=True)

from src.world_economics.tools.serper_tool import serper_tool

# Main Header
st.markdown("""
<div class="main-header">
    <h1>🌍 World Economics AI</h1>
    <p>Advanced AI-powered economic analysis and insights • Real-time data • Interactive assistance</p>
</div>
""", unsafe_allow_html=True)

# Metrics Dashboard
st.markdown("""
<div class="metric-container">
    <div class="metric-box">
        <div class="metric-value">AI-Powered</div>
        <div class="metric-label">Analysis Engine</div>
    </div>
    <div class="metric-box">
        <div class="metric-value">Global</div>
        <div class="metric-label">Market Coverage</div>
    </div>
</div>
""", unsafe_allow_html=True)

FINAL_REPORT_PATH = "final_report.md"

# Helper function
def load_final_report():
    if os.path.exists(FINAL_REPORT_PATH):
        with open(FINAL_REPORT_PATH, "r") as f:
            return f.read()
    return None

# Enhanced Tabs
tabs = st.tabs(["📘 Report Generator", "💬 Interactive Assistant"])

# --- Tab 1: Report Generator ---
with tabs[0]:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    
    # Two column layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 🧠 Generate Economic Report")
        st.markdown("Ask complex economic questions and get comprehensive AI-powered analysis")
        
        # Enhanced input area
        user_query = st.text_area(
            "Enter your economic question",
            placeholder="e.g., How does the Fed's interest rate policy affect developing economies? What are the implications of inflation on global trade?",
            height=120,
            help="Be specific about the economic topic, region, or time period you're interested in"
        )
        
        # Query examples
        with st.expander("💡 Example Questions"):
            st.markdown("""
            - How do interest rate changes affect emerging markets?
            - What is the impact of inflation on consumer spending patterns?
            - How does geopolitical tension influence global supply chains?
            - What are the economic implications of cryptocurrency adoption?
            - How do trade wars affect international commerce?
            """)
        
        submit = st.button("📊 Generate Comprehensive Report", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("### 📋 Report Features")
        st.markdown("""
        <div class="feature-highlight">
            <strong>🔍 Deep Analysis</strong><br>
            Multi-layered economic insights
        </div>
        <div class="feature-highlight">
            <strong>📊 Data-Driven</strong><br>
            Real-time market information
        </div>
        <div class="feature-highlight">
            <strong>🌐 Global Context</strong><br>
            International perspectives
        </div>
        <div class="feature-highlight">
            <strong>📈 Trend Analysis</strong><br>
            Historical and predictive insights
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Process form submission
    if submit:
        if not user_query.strip():
            st.markdown('<div class="status-card status-warning">⚠️ Please enter a valid economic question to generate a report.</div>', unsafe_allow_html=True)
        else:
            # Progress indicator
            progress_container = st.empty()
            with progress_container:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                try:
                    status_text.text("🔄 Initializing AI analysis...")
                    progress_bar.progress(20)
                    
                    status_text.text("🔍 Gathering economic data...")
                    progress_bar.progress(40)
                    
                    status_text.text("🧠 Processing with AI models...")
                    progress_bar.progress(60)
                    
                    inputs = {
                        "user_query": user_query,
                        "current_year": str(datetime.now().year)
                    }
                    
                    status_text.text("📊 Generating comprehensive report...")
                    progress_bar.progress(80)
                    
                    WorldEconomicsCrew().crew().kickoff(inputs=inputs)
                    
                    progress_bar.progress(100)
                    progress_container.empty()
                    
                    st.markdown('<div class="status-card status-success">✅ Report generated successfully!</div>', unsafe_allow_html=True)
                    st.balloons()
                    
                except Exception as e:
                    progress_container.empty()
                    st.markdown('<div class="status-card status-error">❌ Error generating report</div>', unsafe_allow_html=True)
                    st.error(f"Error details: {e}")
                    with st.expander("🔍 Technical Details"):
                        st.code(traceback.format_exc())

    # Show Report if available
    final_report = load_final_report()
    if final_report:
        st.markdown("---")
        
        # Report header with actions
        report_col1, report_col2, report_col3 = st.columns([2, 1, 1])
        
        with report_col1:
            st.markdown("### 📄 Economic Analysis Report")
        
        with report_col2:
            st.markdown(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        with report_col3:
            with open(FINAL_REPORT_PATH, "r") as f:
                st.download_button(
                    "📥 Download Report",
                    f.read(),
                    file_name=f"world_economics_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                    mime="text/markdown",
                    use_container_width=True
                )
        
        # Display report in styled container
        st.markdown('<div class="report-container">', unsafe_allow_html=True)
        st.markdown(final_report, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --- Tab 2: Interactive Assistant ---
with tabs[1]:
    st.markdown('<div class="tab-content">', unsafe_allow_html=True)
    
    final_report = load_final_report()

    if not final_report:
        st.markdown('<div class="status-card status-info">📘 Please generate a report first in the \'Report Generator\' tab to unlock the interactive assistant.</div>', unsafe_allow_html=True)
        
        # Show features while waiting
        st.markdown("### 🤖 Interactive Assistant Features")
        feature_col1, feature_col2 = st.columns(2)
        
        with feature_col1:
            st.markdown("""
            **📊 Report Analysis**
            - Deep dive into specific sections
            - Clarify complex concepts
            - Request additional context
            """)
        
        with feature_col2:
            st.markdown("""
            **🔍 Live Research**
            - Real-time data updates
            - Current market conditions
            - Latest economic news
            """)
    else:
        st.markdown("### 💬 Interactive Economic Assistant")
        st.markdown("Ask follow-up questions about your report or request real-time economic updates")
        
        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Chat interface
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display chat history
        for role, msg in st.session_state.chat_history:
            with st.chat_message(role):
                st.markdown(msg)
        
        # Chat input
        follow_up = st.chat_input("Ask a follow-up question about the report or request current economic data...")

        if follow_up:
            # Add user message to chat
            st.session_state.chat_history.append(("user", follow_up))
            
            with st.chat_message("user"):
                st.markdown(follow_up)
            
            with st.chat_message("assistant"):
                with st.spinner("🤖 Analyzing your question..."):
                    try:
                        # Define inline agent
                        chat_agent = Agent(
                            role="Economic Report Assistant",
                            goal="Answer follow-up questions based on the economic report and provide current economic insights.",
                            backstory="You are an expert economic analyst trained to provide detailed, accurate responses based on economic reports and real-time data.",
                            tools=[serper_tool],
                            verbose=True
                        )

                        # Define task using context
                        chat_task = Task(
                            description=f"""Based on the economic report:

{final_report}

Answer the user's question: {follow_up}

If the question can be answered from the report context, provide a detailed response.
If additional current information is needed, use the search tool to find up-to-date data.
Provide a comprehensive and informative answer.""",
                            expected_output="A detailed, clear, and informative response that addresses the user's question with relevant economic insights.",
                            agent=chat_agent
                        )

                        # Run the crew
                        chat_crew = Crew(
                            agents=[chat_agent],
                            tasks=[chat_task],
                            process=Process.sequential
                        )
                        
                        response = chat_crew.kickoff()
                        
                        # Display response
                        st.markdown(response)
                        
                        # Add to chat history
                        st.session_state.chat_history.append(("assistant", response))

                    except Exception as e:
                        error_msg = f"❌ Error processing your question: {str(e)}"
                        st.error(error_msg)
                        st.session_state.chat_history.append(("assistant", error_msg))
                        
                        with st.expander("🔍 Technical Details"):
                            st.code(traceback.format_exc())
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick action buttons
        if st.session_state.chat_history:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear Chat History", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
            
            with col2:
                if st.button("💾 Export Chat", use_container_width=True):
                    chat_export = "\n\n".join([f"**{role.title()}:** {msg}" for role, msg in st.session_state.chat_history])
                    st.download_button(
                        "📥 Download Chat History",
                        chat_export,
                        file_name=f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )

    st.markdown('</div>', unsafe_allow_html=True)
