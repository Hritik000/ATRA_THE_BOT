# Security Policy

## Reporting Security Vulnerabilities

The ATRA team takes the security and safety of our systems seriously. If you believe you have discovered a vulnerability or security risk, please report it responsibly.

**Please DO NOT report security issues via public GitHub issues, discussions, or pull requests.**

Instead, please send an encrypted email with details to:
- **Email**: security@atra-platform.com or contact repository maintainers privately via GitHub Security Advisories.

Please include:
- A detailed description of the vulnerability.
- Steps to reproduce or proof-of-concept code.
- Impact assessment (affected versions, components).
- Any proposed remediation if known.

We will acknowledge receipt within 48 hours and provide updates throughout the resolution process.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

## Security Principles & System Boundaries

### 1. External Execution Boundary (Quotex Policy)
- ATRA is an analytical and quantitative research platform.
- **ATRA strictly does not automate trade execution** on Quotex or any platform that forbids automated operations.
- The platform operates strictly in analysis, probabilistic signal generation, backtesting, paper trading, and human-in-the-loop review.
- Automated browser clicking, DOM manipulation, CAPTCHA bypassing, private API reverse engineering, and credential replay are prohibited by design.

### 2. Secret & Credential Protection
- Never commit credentials, `.env` files, API keys, tokens, or production dumps.
- All secrets must be injected via environment variables or secret management services.
- The repository includes pre-commit hooks and CI secret scanning to prevent accidental credential leakage.

### 3. Fail-Closed Risk Controls
- The risk engine runs independently of ML models and research agents.
- In any unexpected system state, network partition, or data invalidation, risk controls fail closed (preventing any trade recommendation or action).
