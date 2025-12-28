# Strategy Lifecycle State Machine (SLSM) - The Immune System 

**Status**: Active 
**Role**: Governance / Defense System 
**Philosophy**: Biological Defense, Deterministic, Anti-Fragile 

## Overview 
The SLSM acts as the immune system for the trading brain. It manages the lifecycle of every strategy from birth (Shadow Mode) to death (Retired), ensuring that only fit, robust, and regime-aligned strategies are allowed to interact with real capital or publish content. 

## Core Components 

### 1. SLSM Governor (`agents/slsm_governor.py`) 
The engine logic that: 
- Maintains the registry of all `StrategyDNA`. 
- Evaluates transitions (`evaluate_transitions`). 
- Enforces decay logic (`_apply_confidence_decay`). 
- Handles feedback loops (`report_outcome`). 

### 2. Strategy DNA (`core/slsm_schema.py`) 
The immutable identity of a strategy. 
- **Regime Tags**: "Trends", "Ranging", "High Vol". 
- **States**: SHADOW_MODE, ACTIVE, QUARANTINE, etc. 
- **Lineage**: Source of origin (Human/AI). 

## Lifecycle States 
1. **DORMANT**: Newly ingested. No signals. 
2. **SHADOW_MODE**: "Paper Trading" internally. Invisible to User. Used for validation. 
3. **EXPERIMENTAL**: Visible to User but capped risk. Labelled "Under Evaluation". 
4. **PROBATION**: High scrutiny. Transition state to Active. 
5. **ACTIVE**: Full permissions. 
6. **QUARANTINE**: Failed a safety check (e.g. 3 losses in a row). Under Autopsy. 
7. **DEGRADED**: Cooling off. 
8. **SUSPENDED**: Regime mismatch (e.g. Trend strategy in Ranging market). 
9. **RETIRED**: Obsolete. 

## Usage in The General 
The General delegates lifecycle management to the SLSM. 

```python 
from app.services.the_general.main_governor import the_general 

# 1. Register a new strategy (Starts in Shadow) 
the_general.register_new_strategy(my_strategy_dna) 

# 2. Periodically Evaluate (e.g. Daily or Post-Trade) 
new_state = the_general.evaluate_strategy_lifecycle("STRAT_001", MarketRegime.TRENDING_HIGH_VOL) 
``` 

## Transition Rules 
- **Shadow -> Experimental**: >80% Merit + >10 samples. 
- **Active -> Quarantine**: 3 Consecutive Losses. 
- **Any -> Suspended**: Market Regime does not match Strategy Tags. 
- **Inactivity**: Confidence decays if not used for >2 days. 
