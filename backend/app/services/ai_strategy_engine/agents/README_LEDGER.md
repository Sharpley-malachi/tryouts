# The Truth Ledger - The Immutable Memory 

**Status**: Active 
**Role**: Epistemic Backbone / Verifiable Reality 
**Philosophy**: Immutable, Append-Only, Hash-Chained 

## Overview 
The Truth Ledger ensures that the system's history cannot be rewritten. It records every thought, decision, and outcome in a cryptographically verifiable chain. It prevents hindsight bias and provides the "Legal Discovery" layer for the AI. 

## Architecture 
A Hybrid Local Ledger: 
1.  **Storage (Layer 1)**: `data/ledger/truth_ledger.jsonl`. A human-readable, append-only JSON file where every line is a hash-linked block. 
2.  **Indexing (Layer 2)**: `data/ledger/ledger_index.db`. An SQLite database for fast queries and reconstruction. 

## Schema (`core/ledger_schema.py`) 
Each entry contains: 
- `event_type`: DAE_INTERLOCK, PATTERN_DISCOVERED, etc. 
- `payload`: The actual data. 
- `prev_hash`: The hash of the previous line (The Chain). 
- `hash`: SHA-256(prev_hash + timestamp + payload). 

## Usage in The General 
The General automatically logs specific high-value events. 

```python 
from app.services.ai_strategy_engine.core.truth_ledger import truth_ledger, LedgerEventType 

# Record an event 
hash = truth_ledger.record_event( 
    LedgerEventType.PATTERN_DISCOVERED, 
    { 
        "pattern": "Bullish Engulfing", 
        "confidence": 0.85 
    } 
) 
``` 

## Audit & Reconstruction 
You can reconstruct the system's "belief state" at any past timestamp using `reconstruct_state_at_timestamp(ts)`. This proves what the AI knew (and didn't know) at that moment. 

## Files 
- `core/truth_ledger.py`: The engine. 
- `core/ledger_schema.py`: Event definitions. 
- `data/ledger/`: Storage location (Created on first run). 
