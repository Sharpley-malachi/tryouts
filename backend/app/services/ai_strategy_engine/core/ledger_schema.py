from enum import Enum 
from typing import Dict, Any, Optional, List 
from dataclasses import dataclass, field 
from datetime import datetime, timezone 
import hashlib 
import json 

# --- Enums --- 

class LedgerEventType(str, Enum): 
    # System Lifecycle 
    GENESIS_SYNC = "GENESIS_SYNC" 
    
    # Governance 
    DAE_INTERLOCK = "DAE_INTERLOCK" 
    STRATEGY_QUARANTINE = "STRATEGY_QUARANTINE" 
    STRATEGY_STATE_CHANGED = "STRATEGY_STATE_CHANGED" 
    STRATEGY_EVALUATED = "STRATEGY_EVALUATED" 
    
    # Intelligence 
    DATA_INGESTED = "DATA_INGESTED" 
    PATTERN_DISCOVERED = "PATTERN_DISCOVERED" 
    DISCOVERY_CERTIFICATION = "DISCOVERY_CERTIFICATION" 
    PREDICTION_ISSUED = "PREDICTION_ISSUED" 
    
    # Feedback & Outcomes 
    FEEDBACK_RECEIVED = "FEEDBACK_RECEIVED" 
    OUTCOME_RECORDED = "OUTCOME_RECORDED" 
    ANOMALY_FLAGGED = "ANOMALY_FLAGGED" 
    
    # Knowledge 
    EBOOK_SNAPSHOT = "EBOOK_SNAPSHOT" 
    KNOWLEDGE_PUBLISHED = "KNOWLEDGE_PUBLISHED" 
    
    # Technical 
    SYSTEM_ERROR = "SYSTEM_ERROR" 

class AssetClass(str, Enum): 
    FOREX_ONLY = "FOREX_ONLY" 
    INDICES_ONLY = "INDICES_ONLY" 
    MIXED_ERR = "MIXED_ERR" 

# --- Nested Schemas --- 

@dataclass 
class TemporalAnchor: 
    """ 
    Locks the 4H, Daily, Weekly, and Monthly timestamps together. 
    """ 
    t_4h: Optional[str] = None 
    t_daily: Optional[str] = None 
    t_weekly: Optional[str] = None 
    t_monthly: Optional[str] = None 

@dataclass 
class CausalityLink: 
    """ 
    Lineage tracking. 
    """ 
    initiating_agent_id: str 
    input_data_hash: str 
    logic_version_hash: Optional[str] = None 
    model_weights_hash: Optional[str] = None 

# --- Root Object --- 

@dataclass 
class EpistemicBlock: 
    """ 
    The Atomic Contract of Reality. 
    Corresponds to the 'TruthLedgerEntry' requirements. 
    """ 
    event_type: LedgerEventType 
    payload: Dict[str, Any] 
    
    # Header 
    prev_hash: str 
    block_height: int 
    utc_correlation_id: str 
    
    # Causality & Truth 
    causality: CausalityLink 
    temporal_anchor: TemporalAnchor 
    
    # Metadata generated at creation 
    entry_id: str = field(default_factory=lambda: "") 
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat()) 
    hash: str = field(default_factory=lambda: "") 
    
    # Merkle Proof Context 
    merkle_root_snapshot: Optional[str] = None 

    def calculate_hash(self) -> str: 
        """ 
        Calculates the SHA-256 hash using Canonical sorting. 
        """ 
        data_to_hash = { 
            "prev": self.prev_hash, 
            "height": self.block_height, 
            "utc": self.utc_correlation_id, 
            "ts": self.timestamp_utc, 
            "type": self.event_type.value, 
            "payload": self.payload, 
            "causality": self.causality.__dict__, 
            "anchor": self.temporal_anchor.__dict__ 
        } 
        # Canonical Sort 
        block_string = json.dumps(data_to_hash, sort_keys=True, separators=(',', ':')) 
        return hashlib.sha256(block_string.encode()).hexdigest() 

    def to_dict(self) -> Dict[str, Any]: 
        return { 
            "entry_id": self.entry_id, 
            "hash": self.hash, 
            "prev_hash": self.prev_hash, 
            "block_height": self.block_height, 
            "utc_correlation_id": self.utc_correlation_id, 
            "timestamp_utc": self.timestamp_utc, 
            "event_type": self.event_type.value, 
            "payload": self.payload, 
            "causality": self.causality.__dict__, 
            "temporal_anchor": self.temporal_anchor.__dict__, 
            "merkle_root_snapshot": self.merkle_root_snapshot 
        } 
