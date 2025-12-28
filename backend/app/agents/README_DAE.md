# Decision Authorization Engine (DAE) -- The Constitutional Layer 
**Status**: Active 
**Role**: Governance Kernel / Supreme Court 
**Philosophy**: Zero-Trust, Deterministic, Fail-Closed 

## Overview 
The Decision Authorization Engine (DAE) is a non-AI, rule-based system designed to sit between the Intelligence layers (AI Agents) and the Action layers (Execution/Publication). It ensures that no action is taken without explicit, auditable authorization. 

## Core Components 

### 1. DecisionAuthorizationEngine (`agents/decision_engine.py`) 
The main engine class. It: 
- Accepts a `DecisionContext`. 
- Iterates through a set of composable `Rules`. 
- Returns a `DecisionOutput` (APPROVED/REJECTED). 
- Generates cryptographic Audit Hashes. 

### 2. Decision Context Schema (`core/dae_schema.py`) 
A strict JSON-compatible schema that defines the input required for a decision. Signals from multiple agents must be mapped to this schema. 
Includes: 
- **Identity**: Request IDs, Originating Agent. 
- **Integrity**: Data completeness, temporal alignment, drift. 
- **Strategy State**: Status, historical win rate. 
- **risk_signals**: R:R ratio, confidence scores. 

### 3. Governance Rules (`core/dae_rules.py`) 
Independent, hot-reloadable logic blocks. 
- **DataDriftRule**: Rejects if human latency drift > 5 pips (varies by timeframe) or data is stale (>15 mins). 
- **ConfidenceGatingRule**: Enforces thresholds (e.g., > 0.85 for IRONCLAD mode). 
- **RiskRewardRule**: Enforces minimum R:R logic. 
- **StrategySanityRule**: Prevents execution of RETIRED strategies. 
- **EducationalIntegrityRule**: Specific gates for eBook content (No hype words, Forex/Indices separation). 

## Usage 
In `main_governor.py`, the `TheGeneral` class has been updated to include the DAE. 
```python 
from agents.decision_engine import DecisionAuthorizationEngine 
from core.dae_schema import SafetyLevel 

# Initialize 
dae = DecisionAuthorizationEngine(SafetyLevel.CONSERVATIVE) # Levels: EXPERIMENTAL, CONSERVATIVE, IRONCLAD 

# Request Authorization 
decision = dae.authorize(context) 

if decision.authorization_status == "APPROVED": 
    execute_trade(decision.auth_token) 
else: 
    log_failure(decision.violated_rules) 
``` 

## Failure Modes 
The DAE is designed to **Fail Closed**. 
- If data is missing -> REJECT. 
- If rules conflict -> REJECT. 
- If drift is high -> REJECT. 

## Auditability 
Every decision produces an `audit_hash` and `auth_token` (if approved). These should be logged to the immutable ledger (e.g., Firebase) to ensure full decision replay capability. 
