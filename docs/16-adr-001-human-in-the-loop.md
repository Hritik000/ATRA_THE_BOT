# ADR-001: Human-in-the-Loop External Execution

## Status
Accepted

## Context
ATRA generates market research signals. Quotex's published rules prohibit automated mechanisms/algorithms/specialized software performing operations without direct client participation.

## Decision
ATRA will not implement automated Quotex execution, browser clicking, CAPTCHA bypass, session hijacking, or reverse-engineered private execution interfaces.

Allowed:
- market analysis
- research signals
- notifications
- paper trading
- manual confirmation

## Consequences
The platform remains reusable as a research system and avoids prohibited automation, but external execution remains manual.

## Revisit
Only if the platform publishes an authorized automation/API mechanism and explicitly permits the intended use.
