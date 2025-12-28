# AI #2 — Strategy Interpretation & Logic Compiler Engine

## Overview
This system acts as a Translator and Sanitizer between "Narrative Logic" (human videos/ideas) and "Executable Mathematics" (the trading engine). It ingests raw strategy definitions (JSON/Python), normalizes them into a standard structure, deduplicates overlapping logic, evaluates them against the current market context (provided by AI #1), and scores them for execution.

## Directory Structure
```
ai_strategy_engine/
├── config.py               # Configuration and Constants
├── core_types.py           # Data Classes (The "DNA": Strategy, LogicBlock, etc.)
├── main.py                 # The Orchestrator (Entry Point)
├── agents/                 # The Sub-Agents of the Swarm
│   ├── ingestor.py         # Parses strategy files
│   ├── normalizer.py       # Standardizes logic, removes narrative
│   ├── deduplicator.py     # Merges identical strategies based on logic hash
│   ├── context_evaluator.py# Checks Market Regime (Trends, Time)
│   └── scorer.py           # Calculates Logic Scores & Conflicts
└── knowledge_base/         
    └── strategies/         # Specific Strategy Implementations
        ├── ep1_pd_arrays.py
        ├── ep2_market_structure.py
        ├── ep3_order_flow.py
        ├── ep4_candle_science.py
        ├── ep5_narrative.py
        ├── ep6_fvgs.py
        ├── ep7_fva_ranking.py
        ├── ep8_liquidity.py
        └── multi_layer_context.py
```

## How to Run the Engine
To run the main interpretation engine which loads strategies, dedupes them, and evaluates them against a mock market state:

```bash
python ai_strategy_engine/main.py
```

## How to Run Individual Strategies
Each strategy file in `knowledge_base/strategies` is a standalone module that can run a backtest on synthetic data.

Example:
```bash
python ai_strategy_engine/knowledge_base/strategies/ep1_pd_arrays.py
```

## Architecture Details

### 1. Ingestion (Agents/Ingestor)
Simulates loading raw JSON/Python code generated from video analysis.

### 2. Normalization (Agents/Normalizer)
Converts raw inputs into `NormalizedStrategy` objects. It strips away "narrative" names (e.g., "Banker Candle") and maps them to standard Logic Blocks (e.g., `formation_opposing_fvg`).

### 3. Deduplication (Agents/Deduplicator)
Hashes the logic blocks of each strategy. If two strategies have different names but identical logic (e.g., "Vid 1 Strategy" vs "Vid 5 Strategy"), they are merged to prevent redundant signals.

### 4. Context Evaluation (Agents/ContextEvaluator)
Acts as the bridge to AI #1. It penalizes strategies that do not fit the current regime (e.g., Trend Following in a Choppy Market).

### 5. Scoring (Agents/Scorer)
Final decision maker. Calculates confidence scores, detects conflicts (Strategy A says Long, Strategy B says Short), and looks for confluence.

## Dependencies
- pandas
- numpy
