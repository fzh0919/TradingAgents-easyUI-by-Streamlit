import streamlit as st
import streamlit.components.v1 as stc
import datetime
import os
import time
from dotenv import load_dotenv
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.llm_clients.model_catalog import MODEL_OPTIONS
from cli.stats_handler import StatsCallbackHandler

load_dotenv()


def update_env_file(key_data: dict):
    """Persist API keys to .env and update os.environ."""
    env_path = ".env"
    existing_lines = []
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            existing_lines = f.readlines()
    env_dict = {}
    for line in existing_lines:
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            env_dict[k.strip()] = v.strip()
    for k, v in key_data.items():
        if v:
            env_dict[k] = v
            os.environ[k] = v
    with open(env_path, "w", encoding="utf-8") as f:
        f.write("# LLM Providers and Data API keys (Set via Web UI)\n")
        for k, v in env_dict.items():
            f.write(f"{k}={v}\n")


# ---- Page Config ----
st.set_page_config(
    page_title="TradingAgents - Multi-Agent Intelligence",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    /* Global font unification (Careful not to override Streamlit Material Icons in spans/divs) */
    body, p, li, ul, ol, a, .stMarkdown {
        font-family: 'Inter', 'Google Sans', 'Outfit', sans-serif !important;
    }
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Google Sans', 'Outfit', 'Inter', sans-serif !important;
        color: #202124;
    }
    h1 { font-weight: 700; }
    h2, h3, h4, h5, h6 { font-weight: 600; color: #3c4043; }
    
    .top-gradient {
        height: 6px;
        background: linear-gradient(90deg, #4285F4 0%, #EA4335 25%, #FBBC05 50%, #34A853 75%, #4285F4 100%);
        border-radius: 3px; margin-bottom: 2rem;
    }
    .premium-card {
        background: #ffffff; border-radius: 12px; padding: 24px;
        border: 1px solid #e0e0e0; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 1.5rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .premium-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    }
    .blue-text { color: #4285F4; font-weight: 600; }
    .green-text { color: #34A853; font-weight: 600; }
    .red-text { color: #EA4335; font-weight: 600; }
    .stTabs [data-baseweb="tab-list"] { gap: 16px; }
    .stTabs [data-baseweb="tab"] {
        height: 48px; white-space: pre-wrap; background-color: #f1f3f4;
        border-radius: 8px 8px 0 0; padding: 10px; font-weight: 600; color: #5f6368;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e8f0fe; color: #1a73e8 !important;
        border-bottom: 3px solid #1a73e8;
    }
    </style>
    <div class="top-gradient"></div>
    """,
    unsafe_allow_html=True,
)

# ---- Header ----
hcol1, hcol2 = st.columns([1, 10])
with hcol1:
    st.markdown("<h1 style='font-size:3.5rem;margin-top:-10px'>📈</h1>", unsafe_allow_html=True)
with hcol2:
    st.markdown(
        "<h1 style='margin:0;padding:0'>TradingAgents Platform</h1>"
        "<p style='color:#5f6368;font-size:1.1rem;margin-top:2px'>"
        "Multi-Agent LLM Financial Trading Framework</p>",
        unsafe_allow_html=True,
    )

st.markdown(
    "<div class='premium-card'><p style='margin:0;color:#202124'>"
    "Run multi-agent trading simulations by specifying a ticker symbol and selecting active agents. "
    "The system performs deep analysis, debates the options, and issues a structured investment decision."
    "</p></div>",
    unsafe_allow_html=True,
)

# ==================== SIDEBAR ====================
st.sidebar.markdown(
    "<h2 style='text-align:center;margin-bottom:1rem;color:#202124'>🔧 Configuration</h2>",
    unsafe_allow_html=True,
)

st.sidebar.markdown("<p class='blue-text' style='margin-bottom:2px'>LLM Options</p>", unsafe_allow_html=True)
provider = st.sidebar.selectbox(
    "Provider",
    ["openai", "google", "anthropic", "xai", "deepseek", "qwen", "glm", "openrouter", "ollama", "azure"],
    index=4,
)
ticker = st.sidebar.text_input("Ticker Symbol", value="NVDA", max_chars=12).upper().strip()


def get_model_choices(prov: str, mode: str) -> list:
    prov_lower = prov.lower()
    if prov_lower in MODEL_OPTIONS and mode in MODEL_OPTIONS[prov_lower]:
        return MODEL_OPTIONS[prov_lower][mode]
    return [("Default Model", "default")]


quick_opts = get_model_choices(provider, "quick")
deep_opts = get_model_choices(provider, "deep")
selected_quick = st.sidebar.selectbox("Quick Thinking Model", options=[o[0] for o in quick_opts])
selected_deep = st.sidebar.selectbox("Deep Thinking Model", options=[o[0] for o in deep_opts])
quick_think_llm = next((o[1] for o in quick_opts if o[0] == selected_quick), "default")
deep_think_llm = next((o[1] for o in deep_opts if o[0] == selected_deep), "default")
if quick_think_llm in ("custom", "default"):
    quick_think_llm = st.sidebar.text_input("Enter Custom Quick Model ID", value="")
if deep_think_llm in ("custom", "default"):
    deep_think_llm = st.sidebar.text_input("Enter Custom Deep Model ID", value="")

st.sidebar.markdown("<hr style='margin:12px 0'/>", unsafe_allow_html=True)
analysis_date = st.sidebar.date_input(
    "Analysis Date",
    value=datetime.date.today() - datetime.timedelta(days=1),
    max_value=datetime.date.today(),
)

st.sidebar.markdown("<p class='blue-text' style='margin-bottom:2px'>Analysis Coverage</p>", unsafe_allow_html=True)
ALL_ANALYSTS = ["market", "social", "news", "fundamentals"]
selected_analysts = [a for a in ALL_ANALYSTS if st.sidebar.checkbox(a.capitalize(), value=True)]

st.sidebar.markdown("<hr style='margin:12px 0'/>", unsafe_allow_html=True)
ROUND_LABELS = ["Less", "Default", "More", "Thorough"]
ROUND_VALUES = {"Less": 1, "Default": 2, "More": 3, "Thorough": 5}
debate_level = st.sidebar.selectbox("Debate Rounds", options=ROUND_LABELS, index=0)
risk_level = st.sidebar.selectbox("Risk Assessment Rounds", options=ROUND_LABELS, index=0)
max_debate_rounds = ROUND_VALUES[debate_level]
max_risk_discuss_rounds = ROUND_VALUES[risk_level]
checkpoint_enabled = st.sidebar.checkbox("Enable Checkpointing", value=False)

st.sidebar.markdown("<hr style='margin:12px 0'/>", unsafe_allow_html=True)
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
        update_env_file({
            "OPENAI_API_KEY": openai_key, "GOOGLE_API_KEY": google_key,
            "ANTHROPIC_API_KEY": anthropic_key, "XAI_API_KEY": xai_key,
            "DEEPSEEK_API_KEY": deepseek_key, "DASHSCOPE_API_KEY": dashscope_key,
            "ZHIPU_API_KEY": zhipu_key, "OPENROUTER_API_KEY": openrouter_key,
            "ALPHA_VANTAGE_API_KEY": alpha_key,
        })
        st.success("API Keys saved!")

# ==================== SESSION STATE ====================
if "is_running" not in st.session_state:
    st.session_state.is_running = False
if "cancel_requested" not in st.session_state:
    st.session_state.cancel_requested = False
if "result" not in st.session_state:
    st.session_state.result = None

# ==================== CONSTANTS ====================
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

# Maps state-dict keys to the display name shown in the grid
STATE_KEY_TO_NODE = {
    "market_report": "Market Analyst",
    "sentiment_report": "Social Analyst",
    "news_report": "News Analyst",
    "fundamentals_report": "Fundamentals Analyst",
    "trader_investment_plan": "Trader",
    "investment_plan": "Portfolio Manager",
}


def build_expected_steps(analysts_list, debate_rounds, risk_rounds):
    """Return ordered list of agent display-names for the progress grid."""
    steps = [f"{a.capitalize()} Analyst" for a in analysts_list]
    for _ in range(debate_rounds):
        steps.extend(["Bull Researcher", "Bear Researcher"])
    steps.extend(["Research Manager", "Trader"])
    for _ in range(risk_rounds):
        steps.extend(["Aggressive Analyst", "Conservative Analyst", "Neutral Analyst"])
    steps.append("Portfolio Manager")
    return steps


def detect_completed(chunk, completed_set):
    """Inspect a full-state chunk and return newly-completed node names."""
    newly = []

    # Simple top-level keys
    for state_key, node_name in STATE_KEY_TO_NODE.items():
        if chunk.get(state_key) and node_name not in completed_set:
            newly.append(node_name)

    # Investment debate sub-keys
    inv = chunk.get("investment_debate_state", {})
    if inv.get("bull_history") and "Bull Researcher" not in completed_set:
        newly.append("Bull Researcher")
    if inv.get("bear_history") and "Bear Researcher" not in completed_set:
        newly.append("Bear Researcher")
    if inv.get("judge_decision") and "Research Manager" not in completed_set:
        newly.append("Research Manager")

    # Risk debate sub-keys
    risk = chunk.get("risk_debate_state", {})
    if risk.get("current_aggressive_response") and "Aggressive Analyst" not in completed_set:
        newly.append("Aggressive Analyst")
    if risk.get("current_conservative_response") and "Conservative Analyst" not in completed_set:
        newly.append("Conservative Analyst")
    if risk.get("current_neutral_response") and "Neutral Analyst" not in completed_set:
        newly.append("Neutral Analyst")

    return newly


# ==================== CALLBACKS ====================
def run_analysis():
    st.session_state.is_running = True
    st.session_state.cancel_requested = False
    st.session_state.result = None


def stop_analysis():
    st.session_state.cancel_requested = True


# ==================== BUTTONS ====================
col_run, col_stop = st.columns([4, 1])
with col_run:
    st.button("🚀 Run Analysis Graph", use_container_width=True,
              on_click=run_analysis, disabled=st.session_state.is_running)
with col_stop:
    st.button("⛔ Stop", use_container_width=True,
              on_click=stop_analysis, disabled=not st.session_state.is_running)

# ==================== EXECUTION ====================
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

            # Token/LLM usage tracking (same handler as CLI)
            stats_handler = StatsCallbackHandler()

            # Build graph with stats callback
            ta = TradingAgentsGraph(
                selected_analysts=selected_analysts,
                debug=False,
                config=cfg,
                callbacks=[stats_handler],
            )
            ta.ticker = ticker  # needed by _log_state → safe_ticker_component

            expected_steps = build_expected_steps(
                selected_analysts, max_debate_rounds, max_risk_discuss_rounds
            )
            total_steps = len(expected_steps)

            # ---- Progress UI (native Streamlit widgets only) ----
            progress_bar = st.progress(0)
            metrics_placeholder = st.empty()
            status_container = st.empty()
            grid_placeholder = st.empty()

            completed_list = []   # preserves insertion order
            completed_set = set()
            cancelled = False

            def render_grid():
                """Render agent grid using native st.columns (no CSS grid needed)."""
                cols_per_row = 3
                with grid_placeholder.container():
                    rows = [expected_steps[i:i + cols_per_row]
                            for i in range(0, len(expected_steps), cols_per_row)]
                    for row in rows:
                        cols = st.columns(cols_per_row)
                        for j, step in enumerate(row):
                            icon, desc = "⚙️", step
                            for key, (ic, ds) in NODE_INFO.items():
                                if key in step:
                                    icon, desc = ic, ds
                                    break
                            done = step in completed_set
                            with cols[j]:
                                if done:
                                    st.success(f"{icon} **{step}**\n\n✅ {desc}")
                                else:
                                    st.info(f"{icon} **{step}**\n\n⏳ {desc}")

            def format_tokens(n):
                """Format token count for compact display."""
                if n >= 1_000_000:
                    return f"{n / 1_000_000:.1f}M"
                if n >= 1_000:
                    return f"{n / 1_000:.1f}K"
                return str(n)

            def render_metrics():
                elapsed = time.time() - start_time
                mins, secs = divmod(int(elapsed), 60)
                stats = stats_handler.get_stats()
                with metrics_placeholder.container():
                    mc1, mc2, mc3, mc4 = st.columns(4)
                    mc1.metric("⏱️ Elapsed", f"{mins}m {secs}s")
                    mc2.metric("📊 Progress", f"{len(completed_set)}/{total_steps} agents")
                    tok_label = f"↑{format_tokens(stats['tokens_in'])} ↓{format_tokens(stats['tokens_out'])}" if (stats['tokens_in'] or stats['tokens_out']) else "--"
                    mc3.metric("🪙 Tokens", tok_label)
                    mc4.metric("🤖 LLM Calls", str(stats['llm_calls']))

            # Initial render
            render_grid()
            render_metrics()

            # ---- Prepare graph ----
            ta._resolve_pending_entries(ticker)
            past_context = ta.memory_log.get_past_context(ticker)
            init_state = ta.propagator.create_initial_state(
                ticker, str(analysis_date), past_context=past_context
            )
            args = ta.propagator.get_graph_args()
            # get_graph_args() already sets stream_mode="values"

            if cfg.get("checkpoint_enabled"):
                from tradingagents.graph.checkpointer import (
                    get_checkpointer, thread_id as ckpt_thread_id,
                )
                ta._checkpointer_ctx = get_checkpointer(cfg["data_cache_dir"], ticker)
                saver = ta._checkpointer_ctx.__enter__()
                ta.graph = ta.workflow.compile(checkpointer=saver)
                tid = ckpt_thread_id(ticker, str(analysis_date))
                args.setdefault("config", {}).setdefault("configurable", {})["thread_id"] = tid

            # ---- Stream the graph ----
            final_state = None
            with st.spinner("🔄 Analysis in progress — agents are working..."):
                for chunk in ta.graph.stream(init_state, **args):
                    if st.session_state.cancel_requested:
                        cancelled = True
                        break

                    # With stream_mode="values", each chunk is the complete state dict
                    final_state = chunk

                    # Detect which nodes just completed
                    newly = detect_completed(chunk, completed_set)
                    for n in newly:
                        completed_set.add(n)
                        completed_list.append(n)

                    # Update progress bar
                    pct = min(len(completed_set) / total_steps, 1.0) if total_steps > 0 else 0
                    progress_bar.progress(pct)

                    # Update status banner
                    if completed_list:
                        latest = completed_list[-1]
                        icon, desc = "⚙️", f"{latest} completed"
                        for key, (ic, ds) in NODE_INFO.items():
                            if key in latest:
                                icon, desc = ic, ds
                                break
                        status_container.markdown(
                            f"<div style='padding:12px 16px;background:#e8f0fe;border-radius:8px;"
                            f"border-left:4px solid #4285F4;font-size:1.05rem'>"
                            f"{icon} <b>{latest}</b> — {desc}</div>",
                            unsafe_allow_html=True,
                        )

                    render_grid()
                    render_metrics()

            # ---- Post-stream handling ----
            if cancelled:
                progress_bar.empty()
                status_container.empty()
                grid_placeholder.empty()
                metrics_placeholder.empty()
                st.warning("⚠️ Analysis was stopped by the user.")
                st.session_state.is_running = False
                st.session_state.cancel_requested = False
                if ta._checkpointer_ctx is not None:
                    ta._checkpointer_ctx.__exit__(None, None, None)

            elif final_state is not None:
                # final_state is the complete state dict from the last stream chunk
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

                final_stats = stats_handler.get_stats()
                st.session_state.result = {
                    "final_state": final_state,
                    "signal": signal,
                    "elapsed": elapsed_time,
                    "tokens_in": final_stats["tokens_in"],
                    "tokens_out": final_stats["tokens_out"],
                    "llm_calls": final_stats["llm_calls"],
                    "tool_calls": final_stats["tool_calls"],
                }
                st.session_state.is_running = False
                st.rerun()
            else:
                st.error("Analysis produced no results.")
                st.session_state.is_running = False

        except Exception as e:
            st.session_state.is_running = False
            st.session_state.cancel_requested = False
            st.error(f"An error occurred: {str(e)}")
            st.exception(e)

# ==================== DISPLAY RESULTS ====================
if st.session_state.result is not None:
    res = st.session_state.result
    final_state = res["final_state"]
    signal = res["signal"]
    elapsed = res["elapsed"]
    mins, secs = divmod(int(elapsed), 60)
    tok_in = res.get("tokens_in", 0)
    tok_out = res.get("tokens_out", 0)
    llm_calls = res.get("llm_calls", 0)
    tool_calls = res.get("tool_calls", 0)

    # Stats bar
    sc1, sc2, sc3 = st.columns([1, 1.5, 1])
    sc1.metric("⏱️ Total Time", f"{mins}m {secs}s")
    sc2.metric("🪙 Tokens", f"↑{tok_in:,}  ↓{tok_out:,}")
    sc3.metric("🤖 LLM Calls", str(llm_calls))
    st.success("✅ Analysis completed successfully!")

    tab1, tab2, tab3 = st.tabs(["🎯 Summary & Decision", "📝 Analyst Reports", "💬 Debate & Logic"])

    with tab1:
        st.markdown("<h3 class='blue-text'>Summary Analysis</h3>", unsafe_allow_html=True)

        decision_str = final_state.get("final_trade_decision", "N/A")
        plan_str = final_state.get("investment_plan", "N/A")

        col_sig, col_rec = st.columns([1, 2])
        with col_sig:
            st.markdown("#### 🎯 Core Signal")
            st.info(f"**{signal}**")
        with col_rec:
            st.markdown("#### ⚖️ Final Recommendation")
            st.markdown(decision_str)
        
        st.markdown("---")
        st.markdown("#### 📋 Investment Plan")
        st.markdown(plan_str)

    with tab2:
        st.markdown("<h3 class='blue-text'>Agent Observations</h3>", unsafe_allow_html=True)
        report_map = {
            "market": "Market Report", "sentiment": "Sentiment Report",
            "news": "News Report", "fundamentals": "Fundamentals Report",
        }
        avail = [a for a in selected_analysts if final_state.get(f"{a}_report")]
        if avail:
            sub_tabs = st.tabs([report_map[a] for a in avail])
            for i, a in enumerate(avail):
                with sub_tabs[i]:
                    st.markdown(final_state[f"{a}_report"])
        else:
            st.info("No report details found in the final state.")

    with tab3:
        st.markdown("<h3 class='blue-text'>Agent Debates & Reasoning</h3>", unsafe_allow_html=True)
        inv_st = final_state.get("investment_debate_state", {})
        risk_st = final_state.get("risk_debate_state", {})
        c_inv, c_risk = st.columns(2)
        with c_inv:
            st.markdown("<h4 class='green-text'>Investment Debate</h4>", unsafe_allow_html=True)
            if inv_st.get("history"):
                st.markdown(inv_st["history"])
            else:
                st.info("No investment debate history recorded.")
        with c_risk:
            st.markdown("<h4 class='red-text'>Risk Discussion</h4>", unsafe_allow_html=True)
            if risk_st.get("history"):
                st.markdown(risk_st["history"])
            else:
                st.info("No risk discussion history recorded.")

    st.markdown("<br>", unsafe_allow_html=True)
    c_clear, c_export = st.columns(2)
    with c_clear:
        if st.button("🔄 Clear Results & Start New Analysis", use_container_width=True):
            st.session_state.result = None
            st.rerun()
    with c_export:
        # Build markdown report string
        report_lines = [
            f"# Trading Analysis Report: {ticker}", 
            f"Generated on: {datetime.date.today()}\n",
            f"## 🎯 Core Signal: {signal}\n",
            "## ⚖️ Final Recommendation",
            f"{final_state.get('final_trade_decision', 'N/A')}\n",
            "## 📋 Investment Plan",
            f"{final_state.get('investment_plan', 'N/A')}\n",
            "## 📝 Analyst Reports"
        ]
        
        for a in ["market", "sentiment", "news", "fundamentals"]:
            if final_state.get(f"{a}_report"):
                report_lines.append(f"\n### {a.capitalize()} Report\n{final_state[f'{a}_report']}")
                
        st.download_button(
            label="💾 Export Report as Markdown",
            data="\n".join(report_lines),
            file_name=f"{ticker}_Analysis_Report.md",
            mime="text/markdown",
            use_container_width=True,
        )

# ---- Footer ----
st.markdown("<hr style='margin:30px 0 15px 0'/>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center;color:#5f6368;font-size:0.85rem'>"
    "TradingAgents Web Interface • Beautifully Crafted for Ease of Use</p>",
    unsafe_allow_html=True,
)
