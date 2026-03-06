# National Security Bedrock (Phase 30)
## Threat Model & Access Governance

### 1. Attacker Scenarios
- **Scenario A: Social Engineering on Officers**
  - Defense: Mandatory Hardware MFA (FIDO2) for National Command.
- **Scenario B: Data Exfiltration by Insider**
  - Defense: ABAC (Attribute-Based Access Control) + PII masking on all analyst screens.
- **Scenario C: Prompt Injection on Honeypots**
  - Defense: Dual-Model Verification (Guardian Model filter).

### 2. Encryption Strategy
- **Data at Rest**: AES-256-GCM via AWS/Cloud KMS.
- **Data in Transit**: TLS 1.3 only; HSTS enforced.

### 3. API Security
- JWT with short-lived (15 min) TTL.
- Mandatory API Key rotation every 30 days for TSP/Bank partners.
