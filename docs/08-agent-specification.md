# Multi-Agent Specification

## Principle
Agents orchestrate tools and research workflows. Deterministic code performs calculations.

## Agents
- Orchestrator: routes tasks and enforces workflow.
- Data Agent: validates datasets.
- Technical Agent: summarizes indicators.
- Regime Agent: classifies regimes.
- Prediction Agent: invokes registered ML models.
- Risk Agent: evaluates risk policy.
- Backtest Agent: executes approved backtest jobs.
- Research Agent: summarizes experiments and proposes hypotheses.

## Tool permissions
Agents use allowlisted typed tools. No agent receives raw Quotex credentials, unrestricted filesystem/network, arbitrary shell execution, or unrestricted database writes.

## Example output
```json
{
  "agent": "risk_agent",
  "status": "success",
  "decision": "BLOCK",
  "reason_codes": ["HIGH_VOLATILITY"],
  "evidence": [],
  "trace_id": "..."
}
```

## Human approval
Any workflow that could lead to external trade execution terminates at a human approval boundary.
