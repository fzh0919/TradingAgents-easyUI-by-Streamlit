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

# Function to update keys directly in the .env file
def update_env_file(key_data: dict):
    env_path = ".env"
    
    # Read existing lines
    existing_lines = []
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            existing_lines = f.readlines()
            
    # Parse existing keys
    env_dict = {}
    for line in existing_lines:
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env_dict[k.strip()] = v.strip()
            
    # Update with new values
    for k, v in key_data.items():
        if v: # Only update if not empty
            env_dict[k] = v
            os.environ[k] = v # Immediately set in process environment
            
    # Write back to file
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("# LLM Providers and Data API keys (Set via Web UI)\n")
        for k, v in env_dict.items():
            f.write(f"{k}={v}\n")

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

# ----------------- MAIN AREA HEADER -----------------
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

st.sidebar.markdown("<hr style='margin: 12px 0;'/>", unsafe_allow_html=True)

# API Keys in Sidebar
with st.sidebar.expander("⚙️ API Keys"):
    openai_key = st.text_input("OpenAI Key", value=os.getenv("OPENAI_API_KEY", ""), type="password")
    google_key = st.text_input("Google Gemini Key", value=os.getenv("GOOGLE_API_KEY", ""), type="password")
    anthropic_key = st.text_input("Anthropic Key", value=os.getenv("ANTHROPIC_API_KEY", ""), type="password")
    xai_key = st.text_input("xAI Key", value=os.getenv("XAI_API_KEY", ""), type="password")
    deepseek_key = st.text_input("DeepSeek Key", value=os.getenv("DEEPSEEK_API_KEY", ""), type="password")
    dashscope_key = st.text_input("DashScope/Qwen Key", value=os.getenv("DASHSCOPE_API_KEY", ""), type="password")
    zhipu_key = st.text_input("GLM/Zhipu Key", value=os.getenv("ZHIPU_API_KEY", ""), type="password")
    openrouter_key = st.text_input("OpenRouter Key", value=os.getenv("OPENROUTER_API_KEY", ""), type="password")
    alpha_key = st.text_input("Alpha Vantage Key", value=os.getenv("ALPHA_VANTAGE_API_KEY", ""), type="password")

    if st.button("💾 Save API Keys"):
        key_map = {
            "OPENAI_API_KEY": openai_key,
            "GOOGLE_API_KEY": google_key,
            "ANTHROPIC_API_KEY": anthropic_key,
            "XAI_API_KEY": xai_key,
            "DEEPSEEK_API_KEY": deepseek_key,
            "DASHSCOPE_API_KEY": dashscope_key,
            "ZHIPU_API_KEY": zhipu_key,
            "OPENROUTER_API_KEY": openrouter_key,
            "ALPHA_VANTAGE_API_KEY": alpha_key,
        }
        update_env_file(key_map)
        st.success("API Keys saved!")


# ---- Session state for run control ----
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "cancel_requested" not in st.session_state:
    st.session_state.cancel_requested = False
if "result" not in st.session_state:
    st.session_state.result = None

# Node display names and icons for progress tracker
NODE_INFO = {
    "Market Analyst": ("📊", "Examining price data & indicators"),
    "Social Analyst": ("💬", "Gauging public sentiment"),
    "News Analyst": ("📰", "Scanning global news & events"),
    "Fundamentals Analyst": ("📈", "Reviewing financials & balance sheets"),
    "Bull Researcher": ("🐂", "Building optimistic thesis"),
    "Bear Researcher": ("🐻", "Challenging with risk scenarios"),
    "Research Manager": ("🧠", "Synthesizing debate verdict"),
    "Trader": ("💹", "Formulating investment strategy"),
    "Aggressive Analyst": ("🔥", "Pushing for higher returns"),
    "Conservative Analyst": ("🛡️", "Evaluating downside protection"),
    "Neutral Analyst": ("⚖️", "Balancing both perspectives"),
    "Portfolio Manager": ("👔", "Making the final decision"),
}


def build_expected_steps(analysts_list, debate_rounds, risk_rounds):
    """Build the ordered list of visible agent nodes for progress tracking."""
    steps = []
    for a in analysts_list:
        steps.append(f"{a.capitalize()} Analyst")
    for _ in range(debate_rounds):
        steps.append("Bull Researcher")
        steps.append("Bear Researcher")
    steps.append("Research Manager")
    steps.append("Trader")
    for _ in range(risk_rounds):
        steps.append("Aggressive Analyst")
        steps.append("Conservative Analyst")
        steps.append("Neutral Analyst")
    steps.append("Portfolio Manager")
    return steps


def run_analysis():
    st.session_state.is_running = True
    st.session_state.cancel_requested = False
    st.session_state.result = None


def stop_analysis():
    st.session_state.cancel_requested = True


# Button row
col_run, col_stop = st.columns([4, 1])
with col_run:
    st.button(
        "🚀 Run Analysis Graph",
        use_container_width=True,
        on_click=run_analysis,
        disabled=st.session_state.is_running,
    )
with col_stop:
    st.button(
        "⛔ Stop",
        use_container_width=True,
        on_click=stop_analysis,
        disabled=not st.session_state.is_running,
    )

# ---- Execution Logic ----
if st.session_state.is_running and st.session_state.result is None:
    if not ticker:
        st.error("Please enter a valid Ticker symbol.")
        st.session_state.is_running = False
    elif not selected_analysts:
        st.error("Please select at least one analyst.")
        st.session_state.is_running = False
    else:
        st.markdown(f"### Analyzing **{ticker}** on **{analysis_date}**")

        cfg = DEFAULT_CONFIG.copy()
        cfg["llm_provider"] = provider
        if quick_think_llm:
            cfg["quick_think_llm"] = quick_think_llm
        if deep_think_llm:
            cfg["deep_think_llm"] = deep_think_llm
        cfg["max_debate_rounds"] = max_debate_rounds
        cfg["max_risk_discuss_rounds"] = max_risk_discuss_rounds
        cfg["checkpoint_enabled"] = checkpoint_enabled

        try:
            start_time = time.time()

            # Build graph
            ta = TradingAgentsGraph(
                selected_analysts=selected_analysts,
                debug=False,
                config=cfg,
            )

            # Build expected steps for progress grid
            expected_steps = build_expected_steps(
                selected_analysts, max_debate_rounds, max_risk_discuss_rounds
            )
            total_steps = len(expected_steps)

            # ---- Progress UI ----
            progress_bar = st.progress(0)
            metrics_placeholder = st.empty()
            status_container = st.empty()
            grid_placeholder = st.empty()

            completed_nodes = set()
            node_count = 0
            cancelled = False

            def render_grid():
                """Render the agent status grid with green/grey cards."""
                cols_per_row = 3
                html_cards = ""
                for step in expected_steps:
                    icon, desc = "⚙️", step
                    for key, (ic, ds) in NODE_INFO.items():
                        if key in step:
                            icon, desc = ic, ds
                            break

                    if step in completed_nodes:
                        bg = "#e6f4ea"
                        border = "#34A853"
                        text_color = "#1e8e3e"
                        status_icon = "✅"
                    else:
                        bg = "#f1f3f4"
                        border = "#dadce0"
                        text_color = "#80868b"
                        status_icon = "⏳"

                    html_cards += f"""
                    <div style='background:{bg}; border: 1px solid {border}; border-radius: 10px;
                                padding: 12px 14px; text-align: center; min-height: 80px;
                                display: flex; flex-direction: column; justify-content: center;'>
                        <div style='font-size: 1.4rem;'>{icon}</div>
                        <div style='font-weight: 600; color: {text_color}; font-size: 0.85rem; margin-top: 4px;'>{step}</div>
                        <div style='font-size: 0.75rem; color: {text_color}; margin-top: 2px;'>{status_icon} {desc}</div>
                    </div>
                    """

                grid_html = f"""
                <div style='display: grid; grid-template-columns: repeat({cols_per_row}, 1fr);
                            gap: 12px; margin: 16px 0;'>
                    {html_cards}
                </div>
                """
                grid_placeholder.markdown(grid_html, unsafe_allow_html=True)

            def render_metrics():
                elapsed = time.time() - start_time
                mins, secs = divmod(int(elapsed), 60)
                metrics_placeholder.markdown(
                    f"""
                    <div style='display: flex; gap: 24px; margin: 10px 0; flex-wrap: wrap;'>
                        <div style='background: #f8f9fa; border-radius: 8px; padding: 10px 20px; border: 1px solid #e0e0e0;'>
                            ⏱️ <b>Elapsed:</b> {mins}m {secs}s
                        </div>
                        <div style='background: #f8f9fa; border-radius: 8px; padding: 10px 20px; border: 1px solid #e0e0e0;'>
                            📊 <b>Progress:</b> {len(completed_nodes)}/{total_steps} agents
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Initial render
            render_grid()
            render_metrics()

            # Use the standard propagate method but stream for progress
            # We replicate the internal streaming logic from _run_graph
            ta._resolve_pending_entries(ticker)
            past_context = ta.memory_log.get_past_context(ticker)
            init_state = ta.propagator.create_initial_state(
                ticker, str(analysis_date), past_context=past_context
            )
            args = ta.propagator.get_graph_args()

            if cfg.get("checkpoint_enabled"):
                from tradingagents.graph.checkpointer import get_checkpointer, thread_id as ckpt_thread_id
                ta._checkpointer_ctx = get_checkpointer(cfg["data_cache_dir"], ticker)
                saver = ta._checkpointer_ctx.__enter__()
                ta.graph = ta.workflow.compile(checkpointer=saver)
                tid = ckpt_thread_id(ticker, str(analysis_date))
                args.setdefault("config", {}).setdefault("configurable", {})["thread_id"] = tid

            # Stream graph execution for live updates
            # stream_mode="values" gives the full state dict after each node
            final_state = None
            prev_keys = set()
            for chunk in ta.graph.stream(init_state, **args):
                if st.session_state.cancel_requested:
                    cancelled = True
                    break

                # chunk is the full state dict after each node step
                final_state = chunk

                # Detect which node just ran by checking for new/changed state keys
                # Parse node name from messages if available
                msgs = chunk.get("messages", [])
                current_node = None
                if msgs and len(msgs) > 0:
                    last_msg = msgs[-1]
                    if hasattr(last_msg, "name") and last_msg.name:
                        current_node = last_msg.name

                # Also detect completed nodes by checking report fields
                new_keys = set()
                for report_key in ["market_report", "sentiment_report", "news_report", "fundamentals_report"]:
                    if chunk.get(report_key) and report_key not in prev_keys:
                        name_map = {
                            "market_report": "Market Analyst",
                            "sentiment_report": "Social Analyst",
                            "news_report": "News Analyst",
                            "fundamentals_report": "Fundamentals Analyst",
                        }
                        completed_nodes.add(name_map[report_key])
                        new_keys.add(report_key)

                # Check debate states for researcher progress
                inv_debate = chunk.get("investment_debate_state", {})
                risk_debate = chunk.get("risk_debate_state", {})

                if inv_debate.get("bull_history") and "Bull Researcher" not in prev_keys:
                    completed_nodes.add("Bull Researcher")
                if inv_debate.get("bear_history") and "Bear Researcher" not in prev_keys:
                    completed_nodes.add("Bear Researcher")
                if inv_debate.get("judge_decision") and "Research Manager" not in prev_keys:
                    completed_nodes.add("Research Manager")

                if chunk.get("final_trade_decision") and "Trader" not in prev_keys:
                    completed_nodes.add("Trader")

                if risk_debate.get("current_aggressive_response") and "Aggressive Analyst" not in prev_keys:
                    completed_nodes.add("Aggressive Analyst")
                if risk_debate.get("current_conservative_response") and "Conservative Analyst" not in prev_keys:
                    completed_nodes.add("Conservative Analyst")
                if risk_debate.get("current_neutral_response") and "Neutral Analyst" not in prev_keys:
                    completed_nodes.add("Neutral Analyst")

                if chunk.get("investment_plan") and "Portfolio Manager" not in prev_keys:
                    completed_nodes.add("Portfolio Manager")

                prev_keys = prev_keys | new_keys | completed_nodes

                # Update progress bar
                pct = min(len(completed_nodes) / total_steps, 1.0) if total_steps > 0 else 0
                progress_bar.progress(pct)

                # Update status banner with latest active node
                if completed_nodes:
                    latest = list(completed_nodes)[-1]
                    icon, description = "⚙️", f"{latest} completed"
                    for key, (ic, desc) in NODE_INFO.items():
                        if key in latest:
                            icon, description = ic, desc
                            break
                    status_container.markdown(
                        f"<div style='padding: 12px 16px; background: #e8f0fe; border-radius: 8px; "
                        f"border-left: 4px solid #4285F4; font-size: 1.05rem;'>"
                        f"{icon} <b>{latest}</b> — {description}</div>",
                        unsafe_allow_html=True,
                    )

                render_grid()
                render_metrics()

            if cancelled:
                progress_bar.empty()
                status_container.empty()
                grid_placeholder.empty()
                metrics_placeholder.empty()
                st.warning("⚠️ Analysis was stopped by the user.")
                st.session_state.is_running = False
                st.session_state.cancel_requested = False
            elif final_state is not None:
                # Log state + memory (final_state is the complete state dict)
                ta.curr_state = final_state
                ta._log_state(str(analysis_date), final_state)
                ta.memory_log.store_decision(
                    ticker=ticker,
                    trade_date=str(analysis_date),
                    final_trade_decision=final_state["final_trade_decision"],
                )
                if cfg.get("checkpoint_enabled"):
                    from tradingagents.graph.checkpointer import clear_checkpoint
                    clear_checkpoint(cfg["data_cache_dir"], ticker, str(analysis_date))
                    if ta._checkpointer_ctx is not None:
                        ta._checkpointer_ctx.__exit__(None, None, None)

                signal = ta.process_signal(final_state["final_trade_decision"])
                elapsed_time = time.time() - start_time


                progress_bar.progress(1.0)
                status_container.empty()

                st.session_state.result = {
                    "final_state": final_state,
                    "signal": signal,
                    "elapsed": elapsed_time,
                }
                st.session_state.is_running = False
                st.rerun()

        except Exception as e:
            st.session_state.is_running = False
            st.session_state.cancel_requested = False
            st.error(f"An error occurred: {str(e)}")
            st.exception(e)

# ---- Display Results ----
if st.session_state.result is not None:
    result = st.session_state.result
    final_state = result["final_state"]
    signal = result["signal"]

    # Stats bar
    elapsed = result["elapsed"]
    mins, secs = divmod(int(elapsed), 60)
    st.markdown(
        f"""
        <div style='display: flex; gap: 20px; margin: 16px 0; flex-wrap: wrap;'>
            <div class='premium-card' style='flex: 1; min-width: 150px; text-align: center; padding: 16px;'>
                <div style='font-size: 1.8rem;'>⏱️</div>
                <div style='font-weight: 700; color: #202124; font-size: 1.3rem;'>{mins}m {secs}s</div>
                <div style='color: #5f6368; font-size: 0.85rem;'>Total Time</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.success("✅ Analysis completed successfully!")

    tab1, tab2, tab3 = st.tabs(["🎯 Summary & Decision", "📝 Analyst Reports", "💬 Debate & Logic"])

    with tab1:
        st.markdown("<h3 class='blue-text'>Summary Analysis</h3>", unsafe_allow_html=True)

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

        st.markdown(
            f"""
            <div class='premium-card' style='background-color: #e8f0fe; border-left: 6px solid #34A853;'>
                <h4 style='color: #1967d2; margin: 0 0 10px 0;'>Core Processed Signal</h4>
                <p style='font-size: 1.25rem; font-weight: 600; color: #1a73e8;'>{signal}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

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

        report_types = {
            "market": "Market Report",
            "sentiment": "Sentiment Report",
            "news": "News Report",
            "fundamentals": "Fundamentals Report",
        }

        avail_tabs = [report_types[a] for a in selected_analysts if f"{a}_report" in final_state]

        if avail_tabs:
            sub_tabs = st.tabs(avail_tabs)
            idx = 0
            for a in selected_analysts:
                if f"{a}_report" in final_state:
                    with sub_tabs[idx]:
                        rep = final_state[f"{a}_report"]
                        if rep:
                            st.markdown(rep)
                        else:
                            st.info(f"No explicit data produced by the {a} agent.")
                    idx += 1
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

    # Clear results button
    if st.button("🔄 Clear Results & Start New Analysis"):
        st.session_state.result = None
        st.rerun()

# Footer
st.markdown("<hr style='margin: 30px 0 15px 0;'/>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align: center; color: #5f6368; font-size: 0.85rem;'>TradingAgents Web Interface • Beautifully Crafted for Ease of Use</p>",
    unsafe_allow_html=True,
)
