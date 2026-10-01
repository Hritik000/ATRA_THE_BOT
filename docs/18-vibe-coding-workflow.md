# Vibe-Coding Workflow

The AI coding agent is an implementation assistant, not the product owner.

## Golden loop
```text
Understand -> Plan -> Inspect -> Implement -> Test -> Review Diff -> Document -> Commit
```

## Rules
- read relevant docs first
- inspect repository before creating files
- do not invent APIs
- make small changes
- run tests after each logical change
- never overwrite unrelated code
- never expose secrets
- never weaken tests
- update docs when behavior changes

## Stop conditions
Stop and ask the human when credentials, production data, destructive migrations, external trade execution, security-control changes, or major architectural changes are involved.
