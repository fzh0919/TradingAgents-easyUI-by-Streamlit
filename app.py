import streamlit as st
import datetime
import os
import time
from dotenv import load_dotenv
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.llm_clients.model_catalog import MODEL_OPTIONS

# Ensure environment variables are loaded
load_dotenv()

# Setup professional page configuration
st.set_page_config(
    page_title="TradingAgents - Multi-Agent Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Premium design enhancements with Google colors and dynamic aesthetics
st.markdown(
    """
    <style>
    /* Gradient line at the top */
    .top-gradient {
        height: 6px;
        background: linear-gradient(90deg, #4285F4 0%, #EA4335 25%, #FBBC05 50%, #34A853 75%, #4285F4 100%);
        border-radius: 3px;
        margin-bottom: 2rem;
    }
    
    /* Sleek card containers */
    .premium-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #e0e0e0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .premium-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
    }
    
    /* Typography */
    h1 {
        font-family: 'Google Sans', 'Outfit', 'Inter', sans-serif;
        font-weight: 700;
        color: #202124;
    }
    h2, h3 {
        font-family: 'Google Sans', 'Outfit', 'Inter', sans-serif;
        font-weight: 600;
        color: #3c4043;
    }
    
    /* Vibrant colors */
    .blue-text { color: #4285F4; font-weight: 600; }
    .green-text { color: #34A853; font-weight: 600; }
    .red-text { color: #EA4335; font-weight: 600; }
    
    /* Styling Streamlit tabs beautifully */
    .stTabs [data-baseweb="tab-list"] {
        gap: 16px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 48px;
        white-space: pre-wrap;
        background-color: #f1f3f4;
        border-radius: 8px 8px 0px 0px;
        gap: 4px;
        padding-top: 10px;
        padding-bottom: 10px;
        font-weight: 600;
        color: #5f6368;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e8f0fe;
        color: #1a73e8 !important;
        border-bottom: 3px solid #1a73e8;
    }
    </style>
    <div class="top-gradient"></div>
    """,
    unsafe_allow_html=True,
)

# ----------------- SIDEBAR -----------------
st.sidebar.markdown(
    "<h2 style='text-align: center; margin-bottom: 1rem; color: #202124;'>🔧 Configuration</h2>",
    unsafe_allow_html=True,
)

# Provider & Ticker inputs
st.sidebar.markdown("<p class='blue-text' style='margin-bottom: 2px;'>LLM Options</p>", unsafe_allow_html=True)
provider = st.sidebar.selectbox(
    "Provider",
    ["openai", "google", "anthropic", "xai", "deepseek", "qwen", "glm", "openrouter", "ollama", "azure"],
    index=4  # Defaults to deepseek
)

ticker = st.sidebar.text_input("Ticker Symbol", value="NVDA", max_chars=12).upper().strip()

# Helper to fetch dropdown options based on provider
def get_model_choices(prov: str, mode: str) -> list:
    prov_lower = prov.lower()
    if prov_lower in MODEL_OPTIONS and mode in MODEL_OPTIONS[prov_lower]:
        # returns [(display_name, value), ...]
        return MODEL_OPTIONS[prov_lower][mode]
    return [("Default Model", "default")]

quick_opts = get_model_choices(provider, "quick")
deep_opts = get_model_choices(provider, "deep")

# Format options for selectbox
quick_display = [opt[0] for opt in quick_opts]
deep_display = [opt[0] for opt in deep_opts]

# Streamlit Selectbox for Quick & Deep Thinking models
selected_quick_display = st.sidebar.selectbox("Quick Thinking Model", options=quick_display)
selected_deep_display = st.sidebar.selectbox("Deep Thinking Model", options=deep_display)

# Extract actual model IDs from choice
quick_think_llm = next((opt[1] for opt in quick_opts if opt[0] == selected_quick_display), "default")
deep_think_llm = next((opt[1] for opt in deep_opts if opt[0] == selected_deep_display), "default")

# Fallback handling for "custom" option
if quick_think_llm == "custom" or quick_think_llm == "default":
    quick_think_llm = st.sidebar.text_input("Enter Custom Quick Model ID", value="")
if deep_think_llm == "custom" or deep_think_llm == "default":
    deep_think_llm = st.sidebar.text_input("Enter Custom Deep Model ID", value="")

st.sidebar.markdown("<hr style='margin: 12px 0;'/>", unsafe_allow_html=True)

# Date Picker (Defaults to yesterday)
analysis_date = st.sidebar.date_input(
    "Analysis Date",
    value=datetime.date.today() - datetime.timedelta(days=1),
    max_value=datetime.date.today(),
)

# Checklist for analysts
st.sidebar.markdown("<p class='blue-text' style='margin-bottom: 2px;'>Analysis Coverage</p>", unsafe_allow_html=True)
analysts = ["market", "social", "news", "fundamentals"]
selected_analysts = []

for a in analysts:
    if st.sidebar.checkbox(a.capitalize(), value=True):
        selected_analysts.append(a)

st.sidebar.markdown("<hr style='margin: 12px 0;'/>", unsafe_allow_html=True)

# Debate depth mappings
ROUND_LABELS = ["Less", "Default", "More", "Thorough"]
ROUND_VALUES = {"Less": 1, "Default": 2, "More": 3, "Thorough": 5}

# Selectbox using human-readable levels instead of numbers
debate_level = st.sidebar.selectbox("Debate Rounds", options=ROUND_LABELS, index=0)
risk_level = st.sidebar.selectbox("Risk Assessment Rounds", options=ROUND_LABELS, index=0)

max_debate_rounds = ROUND_VALUES[debate_level]
max_risk_discuss_rounds = ROUND_VALUES[risk_level]

# Advanced Configuration
checkpoint_enabled = st.sidebar.checkbox("Enable Checkpointing", value=False)


# ----------------- MAIN AREA -----------------
col1, col2 = st.columns([1, 10])
with col1:
    st.markdown("<h1 style='font-size: 3.5rem; margin-top:-10px;'>📈</h1>", unsafe_allow_html=True)
with col2:
    st.markdown(
        """
        <h1 style='margin:0; padding:0;'>TradingAgents Platform</h1>
        <p style='color: #5f6368; font-size: 1.1rem; margin-top: 2px;'>
            Multi-Agent LLM Financial Trading Framework
        </p>
        """,
        unsafe_allow_html=True,
    )

# Brief Info Box
st.markdown(
    """
    <div class='premium-card'>
        <p style='margin:0; color: #202124;'>
            Run multi-agent trading simulations by specifying a ticker symbol and selecting active agents. 
            The system performs deep analysis, debates the options, and issues a structured investment decision.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Trigger Action Button
if st.button("🚀 Run Analysis Graph", use_container_width=True):
    if not ticker:
        st.error("Please enter a valid Ticker symbol.")
    elif not selected_analysts:
        st.error("Please select at least one analyst.")
    else:
        st.markdown(f"### Running **{ticker}** on **{analysis_date}**...")
        
        with st.spinner("Executing agent nodes, tools, and debates... Please wait."):
            # Construct custom configuration matching TradingAgents DEFAULT_CONFIG pattern
            cfg = DEFAULT_CONFIG.copy()
            cfg["llm_provider"] = provider
            if quick_think_llm:
                cfg["quick_think_llm"] = quick_think_llm
            if deep_think_llm:
                cfg["deep_think_llm"] = deep_think_llm
            cfg["max_debate_rounds"] = max_debate_rounds
            cfg["max_risk_discuss_rounds"] = max_risk_discuss_rounds
            cfg["checkpoint_enabled"] = checkpoint_enabled

            # Build and execute the Graph
            try:
                start_time = time.time()
                ta = TradingAgentsGraph(
                    selected_analysts=selected_analysts,
                    debug=False,
                    config=cfg
                )
                
                final_state, signal = ta.propagate(ticker, str(analysis_date))
                elapsed_time = time.time() - start_time
                
                st.success(f"Analysis completed in {elapsed_time:.2f} seconds!")
                
                # Render state out via tabs
                st.markdown("<div style='height:20px;'></div>", unsafe_allow_html=True)
                tab1, tab2, tab3 = st.tabs(["🎯 Summary & Decision", "📝 Analyst Reports", "💬 Debate & Logic"])
                
                with tab1:
                    st.markdown("<h3 class='blue-text'>Summary Analysis</h3>", unsafe_allow_html=True)
                    
                    # Highlight Final Trade decision
                    decision_str = final_state.get("final_trade_decision", "N/A")
                    st.markdown(
                        f"""
                        <div class='premium-card' style='background-color: #f8f9fa; border-left: 6px solid #4285F4;'>
                            <h4 style='color: #202124; margin: 0 0 10px 0;'>Final Recommendation Summary</h4>
                            <p style='font-size: 1.15rem; font-weight: 500; color: #1a2530;'>{decision_str}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    
                    # Highlight Signal
                    st.markdown(
                        f"""
                        <div class='premium-card' style='background-color: #e8f0fe; border-left: 6px solid #34A853;'>
                            <h4 style='color: #1967d2; margin: 0 0 10px 0;'>Core Processed Signal</h4>
                            <p style='font-size: 1.25rem; font-weight: 600; color: #1a73e8;'>{signal}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                    
                    # Portfolio Manager final investment plan
                    plan_str = final_state.get("investment_plan", "N/A")
                    st.markdown(
                        f"""
                        <div class='premium-card' style='background-color: #f1f8e9;'>
                            <h4 style='color: #33691e;'>Investment Plan</h4>
                            <p style='font-size: 1rem; color: #2e7d32;'>{plan_str}</p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                with tab2:
                    st.markdown("<h3 class='blue-text'>Agent Observations</h3>", unsafe_allow_html=True)
                    
                    # Sub-tabs for each Analyst report
                    report_types = {
                        "market": "Market Report",
                        "sentiment": "Sentiment Report",
                        "news": "News Report",
                        "fundamentals": "Fundamentals Report"
                    }
                    
                    avail_tabs = [report_types[a] for a in selected_analysts if f"{a}_report" in final_state]
                    
                    if avail_tabs:
                        sub_tabs = st.tabs(avail_tabs)
                        for i, a in enumerate(selected_analysts):
                            if f"{a}_report" in final_state:
                                with sub_tabs[i]:
                                    rep = final_state[f"{a}_report"]
                                    if rep:
                                        st.markdown(rep)
                                    else:
                                        st.info(f"No explicit data produced by the {a} agent.")
                    else:
                        st.info("No report details found in the final state.")

                with tab3:
                    st.markdown("<h3 class='blue-text'>Agent Debates & Reasoning</h3>", unsafe_allow_html=True)
                    
                    inv_state = final_state.get("investment_debate_state", {})
                    risk_state = final_state.get("risk_debate_state", {})
                    
                    col_inv, col_risk = st.columns(2)
                    
                    with col_inv:
                        st.markdown("<h4 class='green-text'>Investment Debate</h4>", unsafe_allow_html=True)
                        if inv_state and inv_state.get("history"):
                            for idx, msg in enumerate(inv_state["history"]):
                                st.markdown(f"**Turn {idx+1}:** {msg}")
                        else:
                            st.info("No active investment debate history was recorded.")
                    
                    with col_risk:
                        st.markdown("<h4 class='red-text'>Risk Discussion</h4>", unsafe_allow_html=True)
                        if risk_state and risk_state.get("history"):
                            for idx, msg in enumerate(risk_state["history"]):
                                st.markdown(f"**Turn {idx+1}:** {msg}")
                        else:
                            st.info("No active risk discussion history was recorded.")

            except Exception as e:
                st.error(f"An error occurred while running the TradingAgents Graph: {str(e)}")
                st.exception(e)

# Footer
st.markdown("<hr style='margin: 30px 0 15px 0;'/>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: #5f6368; font-size: 0.85rem;'>TradingAgents Web Interface • Beautifully Crafted for Ease of Use</p>",
    unsafe_allow_html=True,
)
