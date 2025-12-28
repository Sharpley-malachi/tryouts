from enum import Enum 
from typing import List, Optional, Dict, Any 
from dataclasses import dataclass, field 
from datetime import datetime 

class AuthorizationStatus(str, Enum): 
    APPROVED = "APPROVED" 
    REJECTED = "REJECTED" 
    DEFERRED = "DEFERRED" 
    CONDITIONALLY_APPROVED = "CONDITIONALLY_APPROVED" 

class DecisionReasonCode(str, Enum): 
    # Success 
    ALL_CHECKS_PASSED = "ALL_CHECKS_PASSED" 
    # Common Failures 
    DATA_DRIFT_EXCEEDED = "DATA_DRIFT_EXCEEDED" 
    STALE_DATA = "STALE_DATA" 
    LOW_CONFIDENCE = "LOW_CONFIDENCE" 
    RISK_LIMIT_EXCEEDED = "RISK_LIMIT_EXCEEDED" 
    STRATEGY_NOT_ACTIVE = "STRATEGY_NOT_ACTIVE" 
    MISSING_SIGNALS = "MISSING_SIGNALS" 
    TIMEFRAME_CONFLICT = "TIMEFRAME_CONFLICT" 
    PEDAGOGICAL_VIOLATION = "PEDAGOGICAL_VIOLATION" # For eBooks 
    REGIME_MISMATCH = "REGIME_MISMATCH" 
    USER_SAFETY_LOCK = "USER_SAFETY_LOCK" 
    # Technical 
    INTERNAL_ERROR = "INTERNAL_ERROR" 

class StrategyStatus(str, Enum): 
    EXPERIMENTAL = "experimental" 
    PROBATION = "probation" 
    ACTIVE = "active" 
    DEGRADED = "degraded" 
    RETIRED = "retired" 

class TimeframeClass(str, Enum): 
    SCALP = "scalp" 
    SWING = "swing" 
    POSITION = "position" 

class SafetyLevel(str, Enum): 
    EXPERIMENTAL = "EXPERIMENTAL" # Level 1 
    CONSERVATIVE = "CONSERVATIVE" # Level 2 
    IRONCLAD = "IRONCLAD" # Level 3 

@dataclass 
class IdentityLineage: 
    global_correlation_id: str 
    request_id: str 
    originating_agent_id: str 
    strategy_id: str 
    instrument_id: str 
    market_type: str # FOREX | INDICES | STOCKS 
    timeframe: str 
    timestamp_utc: datetime 

@dataclass 
class DataIntegritySignals: 
    data_completeness_score: float # 0.0 to 1.0 
    temporal_alignment_confidence: float 
    drift_pips_logged: float 
    feedback_sample_size: int 
    last_validation_timestamp: datetime 
    human_latency_drift: Optional[float] = 0.0 

@dataclass 
class StrategyState: 
    status: StrategyStatus 
    age_days: int 
    historical_win_rate: float 
    regime_dependency_flag: bool 
    last_failure_cluster_timestamp: Optional[datetime] 
    max_allowed_risk_for_context: float = 0.01 

@dataclass 
class ConfidenceRiskSignals: 
    prediction_confidence: float # 0.0 to 1.0 
    risk_to_reward_ratio: float 
    timeframe_class: TimeframeClass 
    predicted_entry: float 
    predicted_stop_loss: float 
    predicted_take_profit: float 

@dataclass 
class DecisionContext: 
    """ 
    The unified schema for every authorization request. 
    """ 
    identity: IdentityLineage 
    integrity: DataIntegritySignals 
    strategy_state: StrategyState 
    risk_signals: ConfidenceRiskSignals 
    # Overrides 
    human_lock_flag: bool = False 
    learning_frozen_flag: bool = False 
    market_news_blackout_flag: bool = False 
    # eBook/Doc specific 
    pedagogical_integrity_score: Optional[float] = None 
    document_claims: List[str] = field(default_factory=list) 
    # Evidence (hashes) 
    evidence_chain: List[str] = field(default_factory=list) 
    hindsight_audit_hash: Optional[str] = None 

@dataclass 
class DecisionOutput: 
    authorization_status: AuthorizationStatus 
    auth_token: Optional[str] # SHA-256 hash if approved 
    decision_reason_code: DecisionReasonCode 
    decision_reason_human: str 
    violated_rules: List[str] 
    required_future_conditions: List[str] 
    audit_hash: str # Unique hash of this decision 
    authorized_parameters: Dict[str, Any] = field(default_factory=dict)
