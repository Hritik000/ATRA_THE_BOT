# Security, Safety & Compliance

## Quotex
ATRA does not automate Quotex execution. Current published Quotex rules prohibit automated mechanisms/algorithms/specialized software performing operations without direct client participation. Re-check official terms before adding any integration.

## Secrets
- never commit credentials
- never log secrets
- use secret stores in production
- rotate credentials
- least privilege
- secret scanning in CI

## AI coding agent
Exclude `.env`, private keys, credential JSON, production dumps, and tokens from agent context.

Agents should not have unrestricted filesystem/network/credential access.

## API
Authentication, authorization, validation, rate limiting, secure headers, TLS, and audit logs.

## Trading safety
Human-in-the-loop, independent risk engine, paper trading before real-world use, no guaranteed-return claims, no automated loss chasing.
