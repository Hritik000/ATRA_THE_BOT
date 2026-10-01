# Threat Model

## Assets
Datasets, model artifacts, experiment results, DB, credentials, AI provider credentials, source code, audit logs.

## Threats and mitigations

Credential leakage -> secret manager, scanning, no logging, rotation.

Prompt/tool injection -> typed tools, allowlists, approval gates, sandboxing.

Data poisoning -> source validation, checksums, anomaly detection, versioning.

Look-ahead leakage -> timestamp tests and chronological pipelines.

Unauthorized execution -> no Quotex automation, human approval.

Model tampering -> artifact hashes and controlled registry permissions.

API abuse -> authentication, authorization, rate limits, validation.

Audit tampering -> restricted/append-only audit storage where practical.
