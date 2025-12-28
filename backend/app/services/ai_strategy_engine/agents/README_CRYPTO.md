# Cryptographic Verification & Schemas 

**Status**: Active 
**Role**: Verification Layer / Epistemic Spine 
**Philosophy**: Merkle Mountain Ranges, Canonical Serialization 

## Overview 
This layer provides the mathematical proof that the system's history is unaltered. It uses a **Merkle Mountain Range (MMR)** to provide append-only efficiency with instant root hash verification. 

## Schemas (`core/ledger_schema.py`) 
**EpistemicBlock** is the atomic unit. 
- `utc_correlation_id`: Unique time ID. 
- `causality`: Tracks the input data hash. 
- `temporal_anchor`: Locks 4H/Daily/Weekly timelines. 

## Crypto Spine (`core/crypto_spine.py`) 
Implements the MMR logic. 
- `append_leaf()`: Adds data to the Merkle structure. 
- `get_root()`: Returns the current "Truth Root". 
- `_canonical_json()`: Ensures JSON is sorted and strict before hashing. 

## API Integration (`api/endpoints/temporal.py`) 
Provides the **Point-in-Time (PIT)** query engine. 
- Endpoint: `POST /ledger/pit` 
- Returns: `HoverPayload` with a **Merkle Proof**. 
- Used by the Frontend Dashboard to show "Green Shield" verification on candles. 

## Usage in Truth Ledger 
The `truth_ledger.py` automatically appends every new entry to the `crypto_spine`, generating a fresh Merkle Root for every block. 
