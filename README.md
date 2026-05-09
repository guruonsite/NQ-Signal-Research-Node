# NQ-Signal-Research-Node
### Autonomous Evaluation of Institutional Futures Signals

This repository serves as a research node for analyzing **NQ Futures** data using localized Agentic AI. It moves beyond simple technical analysis by utilizing LLMs as "Judge Agents" to validate institutional order flow.

## 🔬 Research Focus
- **Model Benchmarking:** Comparing sub-70B local models (GGUF/EXL2) against institutional signal logic.
- **Hallucination Mitigation:** Implementing **PydanticAI** to force structured, verifiable JSON outputs for trading execution.
- **Latency Analysis:** Measuring the "Tick-to-Thought" speed on an optimized RTX 3090 environment.

## 📊 Evaluation Framework
The node ingests Thinkorswim data logs and outputs a "Confidence Score" based on historical #BASHT alerts and institutional volume clusters.

## Agent / MCP Access

This project is being extended with a read-only MCP server that allows compatible AI agents to query structured NQ signal data.

The MCP layer exposes tools such as:

- `get_latest_nq_signal`
- `get_signals_today`
- `get_feed_status`

The server is intentionally read-only. It does not place trades, connect to brokerage accounts, move stops, modify orders, or execute financial transactions.

Its purpose is to provide structured signal intelligence for:

- AI-agent evaluation
- signal journaling
- dashboard integration
- post-signal performance tracking
- research and paper-trading workflows

# Safety and Scope

This repository is for research, journaling, and educational analysis only.

It does not provide financial advice.  
It does not guarantee trading performance.  
It does not execute trades.  
Users are responsible for their own risk controls, trading decisions, and compliance requirements.
