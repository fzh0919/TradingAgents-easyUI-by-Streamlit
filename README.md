<p align="center">
  <img src="assets/TauricResearch.png" style="width: 60%; height: auto;">
</p>

<div align="center" style="line-height: 1;">
  <a href="https://arxiv.org/abs/2412.20138" target="_blank"><img alt="arXiv" src="https://img.shields.io/badge/arXiv-2412.20138-B31B1B?logo=arxiv"/></a>
  <a href="https://discord.com/invite/hk9PGKShPK" target="_blank"><img alt="Discord" src="https://img.shields.io/badge/Discord-TradingResearch-7289da?logo=discord&logoColor=white&color=7289da"/></a>
  <a href="./assets/wechat.png" target="_blank"><img alt="WeChat" src="https://img.shields.io/badge/WeChat-TauricResearch-brightgreen?logo=wechat&logoColor=white"/></a>
  <a href="https://x.com/TauricResearch" target="_blank"><img alt="X Follow" src="https://img.shields.io/badge/X-TauricResearch-white?logo=x&logoColor=white"/></a>
</div>

---

# TradingAgents: Multi-Agents LLM Financial Trading Framework — Easy UI Edition

> **This is a community fork** of [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) that adds a **Streamlit Web UI** on top of the original CLI-based framework, making the platform accessible to users who prefer a point-and-click experience over the command line.

## ✨ What's New in This Fork

| Feature | Description |
|---------|-------------|
| 🖥️ **Streamlit Web UI** | Full browser-based interface — no terminal needed |
| 📊 **Real-Time Agent Progress Grid** | 3-column card layout showing each agent's completion status (green ✅ / grey ⏳) |
| ⏱️ **Live Metrics** | Elapsed time and agent progress counter update in real-time during analysis |
| ⛔ **Run / Stop Controls** | Start and interrupt analysis with responsive buttons |
| 🔐 **Sidebar API Key Management** | Securely input and persist API keys (masked, saved to `.env`) |
| 🎨 **Google-Themed Premium Design** | Gradient header, card-based layout, smooth tab transitions |
| 🔽 **Model Dropdowns** | Pre-populated model lists from the built-in catalog — no manual typing |
| 📈 **Human-Readable Settings** | Debate & risk rounds shown as "Less / Default / More / Thorough" instead of raw numbers |
| 🚀 **One-Click Launch** | `run.bat` auto-installs dependencies, opens Chrome, and runs the server |

## News
- [2026-05] 🆕 **TradingAgents Easy UI v1.0.0** — Streamlit Web UI launched on this fork. See [Release Notes](#release-notes).
- [2026-04] **TradingAgents v0.2.4** released upstream with structured-output agents, LangGraph checkpoint resume, persistent decision log, and more. See [CHANGELOG.md](CHANGELOG.md).

## TradingAgents Framework

TradingAgents is a multi-agent trading framework that mirrors the dynamics of real-world trading firms. By deploying specialized LLM-powered agents — from fundamental analysts, sentiment experts, and technical analysts, to trader, risk management team — the platform collaboratively evaluates market conditions and informs trading decisions.

<p align="center">
  <img src="assets/schema.png" style="width: 100%; height: auto;">
</p>

> TradingAgents framework is designed for research purposes. Trading performance may vary based on many factors. [It is not intended as financial, investment, or trading advice.](https://tauric.ai/disclaimer/)

### Agent Architecture

| Team | Agents | Role |
|------|--------|------|
| **Analyst Team** | Market · Social · News · Fundamentals | Gather data, compute indicators, assess sentiment |
| **Researcher Team** | Bull Researcher · Bear Researcher | Debate investment thesis from opposing perspectives |
| **Research Manager** | Research Manager | Synthesize the debate into a verdict |
| **Trader** | Trader | Formulate an actionable investment strategy |
| **Risk Management** | Aggressive · Conservative · Neutral Analysts | Evaluate risk from three perspectives |
| **Portfolio Manager** | Portfolio Manager | Make the final buy/hold/sell decision |

## Installation

### Prerequisites

- Python 3.11+ (3.13 recommended)
- An API key for at least one LLM provider

### Quick Start

```bash
# 1. Clone this fork
git clone https://github.com/fzh0919/TradingAgents-easyUI.git
cd TradingAgents-easyUI

# 2. Create a virtual environment
conda create -n tradingagents python=3.13
conda activate tradingagents

# 3. Install the package
pip install .
```

### Required API Keys

Set the API key for your chosen LLM provider. You can do this either via environment variables or through the **Web UI sidebar**:

```bash
export DEEPSEEK_API_KEY=...        # DeepSeek (default provider)
export OPENAI_API_KEY=...          # OpenAI (GPT)
export GOOGLE_API_KEY=...          # Google (Gemini)
export ANTHROPIC_API_KEY=...       # Anthropic (Claude)
export XAI_API_KEY=...             # xAI (Grok)
export DASHSCOPE_API_KEY=...       # Qwen (Alibaba DashScope)
export ZHIPU_API_KEY=...           # GLM (Zhipu)
export OPENROUTER_API_KEY=...      # OpenRouter
export ALPHA_VANTAGE_API_KEY=...   # Alpha Vantage (market data)
```

Or simply copy the example file:
```bash
cp .env.example .env
```

> **💡 Tip:** You can also enter API keys directly in the Web UI sidebar under **⚙️ API Keys** — they are securely saved to `.env` and never committed to git.

## Usage

### 🖥️ Web UI (Recommended)

**Windows — One-click launch:**
```
run.bat
```
This will install dependencies, open your browser to `http://localhost:8501`, and start the Streamlit server in the background.

**Any platform — Manual launch:**
```bash
streamlit run app.py
```

**Using the Web UI:**

1. **Configure** — Select your LLM provider, models, ticker symbol, and analysis date in the sidebar
2. **Set API Keys** — Expand the ⚙️ API Keys section to enter your keys (securely masked)
3. **Run** — Click 🚀 **Run Analysis Graph** and watch the real-time progress grid
4. **Review** — When complete, explore results across three tabs:
   - **🎯 Summary & Decision** — Final recommendation, signal, and investment plan
   - **📝 Analyst Reports** — Detailed reports from each analyst agent
   - **💬 Debate & Logic** — Full investment debate and risk discussion transcripts

### ⌨️ CLI (Original)

The original CLI is still fully functional:
```bash
tradingagents          # installed command
python -m cli.main     # run from source
```

### 🐍 Python API

```python
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "deepseek"
config["deep_think_llm"] = "deepseek-chat"
config["quick_think_llm"] = "deepseek-chat"

ta = TradingAgentsGraph(debug=True, config=config)
_, decision = ta.propagate("NVDA", "2026-05-01")
print(decision)
```

### 🐳 Docker

```bash
cp .env.example .env  # add your API keys
docker compose run --rm tradingagents
```

## Web UI Features

### Real-Time Agent Progress Grid

During analysis, the UI displays a live dashboard showing all agents in a 3×N card grid:

- **Grey cards** (⏳) — agent pending
- **Green cards** (✅) — agent completed
- **Live status banner** — shows which agent is currently active
- **Progress bar** — accurate percentage from 0% to 100% (completes at Portfolio Manager)
- **Elapsed timer** — real-time clock of analysis duration

### Sidebar Configuration

| Setting | Type | Description |
|---------|------|-------------|
| Provider | Dropdown | Choose from 10 LLM providers |
| Quick/Deep Model | Dropdown | Pre-populated from model catalog |
| Ticker Symbol | Text | Any valid stock ticker (e.g., NVDA, AAPL) |
| Analysis Date | Date picker | Defaults to yesterday |
| Analysis Coverage | Checkboxes | Toggle individual analyst agents |
| Debate Rounds | Dropdown | Less / Default / More / Thorough |
| Risk Assessment | Dropdown | Less / Default / More / Thorough |
| Checkpointing | Checkbox | Enable crash-recovery (SQLite-backed) |
| API Keys | Password fields | Securely save to `.env` |

## Persistence & Recovery

### Decision Log

Always on. Each completed run appends to `~/.tradingagents/memory/trading_memory.md`. On the next same-ticker run, TradingAgents fetches the realised return, generates a reflection, and injects lessons into the Portfolio Manager prompt.

### Checkpoint Resume

Opt-in via the sidebar checkbox or `--checkpoint` in CLI. State is saved after each graph node so crashed runs resume from the last successful step.

## Security

- API keys are stored in `.env` which is listed in `.gitignore`
- The `.env` file is **never** committed to version control
- All key inputs in the UI are masked (`type="password"`)

## Upstream Credits

This fork is built on [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents) v0.2.4. All upstream features, CLI, Python API, and Docker support remain fully functional. See [CHANGELOG.md](CHANGELOG.md) for the full upstream history.

## Contributing

Contributions are welcome! Whether it's improving the UI, fixing bugs, or adding features — PRs and issues are appreciated.

## Citation

If you find TradingAgents useful in your research, please cite the original work:

```bibtex
@misc{xiao2025tradingagentsmultiagentsllmfinancial,
      title={TradingAgents: Multi-Agents LLM Financial Trading Framework}, 
      author={Yijia Xiao and Edward Sun and Di Luo and Wei Wang},
      year={2025},
      eprint={2412.20138},
      archivePrefix={arXiv},
      primaryClass={q-fin.TR},
      url={https://arxiv.org/abs/2412.20138}, 
}
```

## License

This project inherits the [Apache 2.0 License](LICENSE) from the upstream repository.
