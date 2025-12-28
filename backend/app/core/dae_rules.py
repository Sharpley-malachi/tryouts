from abc import ABC, abstractmethod 
from typing import List, Tuple 
from datetime import datetime, timezone, timedelta 
from .dae_schema import ( 
    DecisionContext, AuthorizationStatus, DecisionReasonCode, 
    SafetyLevel, StrategyStatus, TimeframeClass 
) 

class DAERule(ABC): 
    """ 
    Abstract base class for all DAE rules. 
    """ 
    @property 
    @abstractmethod 
    def rule_id(self) -> str: 
        pass 

    @property 
    @abstractmethod 
    def description(self) -> str: 
        pass 

    @abstractmethod 
    def evaluate(self, context: DecisionContext, safety_level: SafetyLevel) -> Tuple[bool, str, DecisionReasonCode]: 
        """ 
        Returns: 
        passed (bool): True if rule passed, False otherwise. 
        reason (str): Human readable reason. 
        code (DecisionReasonCode): The specific machine code for failure. 
        """ 
        pass 

class DataDriftRule(DAERule): 
    """ 
    Ensures data is not stale and drift is within acceptable limits. 
    """ 
    rule_id = "R_INTEGRITY_001" 
    description = "Checks for data drift and temporal decay." 

    def evaluate(self, context: DecisionContext, safety_level: SafetyLevel) -> Tuple[bool, str, DecisionReasonCode]: 
        # 1. Check Latency Drift 
        # Strictness depends on timeframe usually, but here we use a general heuristic 
        # or specific values from the prompt logic. 
        # Prompt: "If human_latency_drift greater than allowed... (e.g. 5 pips for 4H scalps)" 
        max_drift_pips = 5.0 # Default strict 
        if context.risk_signals.timeframe_class == TimeframeClass.SWING: 
            max_drift_pips = 15.0 
        
        if context.integrity.human_latency_drift is not None and \
           context.integrity.human_latency_drift > max_drift_pips: 
            return False, f"Data drift {context.integrity.human_latency_drift} pips exceeds limit {max_drift_pips}.", DecisionReasonCode.DATA_DRIFT_EXCEEDED 
        
        # 2. Check Stale State (Global Correlation ID age) 
        # Prompt: "If more than X minutes have passed since CSV upload..." 
        # We assume the ID timestamp is the start. 
        # Max age: 5 mins for experimental, 60 mins for swing, etc. 
        # Let's enforce a strict 15 minute expiration for now as a baseline. 
        current_time = datetime.now(timezone.utc) 
        # Ensure context time is aware 
        ctx_time = context.identity.timestamp_utc 
        if ctx_time.tzinfo is None: 
            ctx_time = ctx_time.replace(tzinfo=timezone.utc) 
            
        age_seconds = (current_time - ctx_time).total_seconds() 
        max_age_seconds = 900 # 15 minutes 
        if context.identity.timeframe == "1m" or context.identity.timeframe == "5m": 
            max_age_seconds = 120 # 2 minutes strict for low TF 
            
        if age_seconds > max_age_seconds: 
            return False, f"Data context is stale. Age: {age_seconds}s (Limit: {max_age_seconds}s).", DecisionReasonCode.STALE_DATA 
            
        return True, "Data integrity checks passed.", DecisionReasonCode.ALL_CHECKS_PASSED 

class RiskRewardRule(DAERule): 
    """ 
    Enforces minimum Risk:Reward ratios based on Safety Level. 
    """ 
    rule_id = "R_RISK_001" 
    description = "Enforces Minimum Risk to Reward Ratios." 

    def evaluate(self, context: DecisionContext, safety_level: SafetyLevel) -> Tuple[bool, str, DecisionReasonCode]: 
        rr_ratio = context.risk_signals.risk_to_reward_ratio 
        # Rules based on Safety Level 
        min_rr = 1.0 
        if safety_level == SafetyLevel.CONSERVATIVE: 
            min_rr = 2.0 # 1:2 
        elif safety_level == SafetyLevel.IRONCLAD: 
            min_rr = 2.5 # Stricter 
        elif safety_level == SafetyLevel.EXPERIMENTAL: 
            min_rr = 1.0 # Loose 
            
        if rr_ratio < min_rr: 
            return False, f"R:R {rr_ratio} is below required {min_rr} for {safety_level.value} mode.", DecisionReasonCode.RISK_LIMIT_EXCEEDED 
            
        return True, "Risk/Reward acceptable.", DecisionReasonCode.ALL_CHECKS_PASSED 

class ConfidenceGatingRule(DAERule): 
    """ 
    Gates actions based on AI confidence scores. 
    """ 
    rule_id = "R_CONFIDENCE_001" 
    description = "Minimum confidence thresholds." 

    def evaluate(self, context: DecisionContext, safety_level: SafetyLevel) -> Tuple[bool, str, DecisionReasonCode]: 
        confidence = context.risk_signals.prediction_confidence 
        required_conf = 0.60 
        if safety_level == SafetyLevel.IRONCLAD: 
            required_conf = 0.85 
        elif safety_level == SafetyLevel.CONSERVATIVE: 
            required_conf = 0.75 
            
        if confidence < required_conf: 
            return False, f"Confidence {confidence:.2f} below threshold {required_conf}.", DecisionReasonCode.LOW_CONFIDENCE 
            
        return True, "Confidence adequate.", DecisionReasonCode.ALL_CHECKS_PASSED 

class StrategySanityRule(DAERule): 
    """ 
    Checks if strategy is active and healthy. 
    """ 
    rule_id = "R_STRATEGY_001" 
    description = "Verifies strategy lifecycle status." 

    def evaluate(self, context: DecisionContext, safety_level: SafetyLevel) -> Tuple[bool, str, DecisionReasonCode]: 
        status = context.strategy_state.status 
        if status == StrategyStatus.RETIRED: 
            return False, "Strategy is RETIRED.", DecisionReasonCode.STRATEGY_NOT_ACTIVE 
        if status == StrategyStatus.DEGRADED and safety_level != SafetyLevel.EXPERIMENTAL: 
            return False, "Strategy is DEGRADED (only allowed in Experimental).", DecisionReasonCode.STRATEGY_NOT_ACTIVE 
            
        # Win rate checks 
        win_rate = context.strategy_state.historical_win_rate 
        if safety_level == SafetyLevel.IRONCLAD and win_rate < 0.55: 
            return False, f"Historical win rate {win_rate} too low for IRONCLAD mode.", DecisionReasonCode.LOW_CONFIDENCE 
            
        return True, "Strategy status valid.", DecisionReasonCode.ALL_CHECKS_PASSED 

class EducationalIntegrityRule(DAERule): 
    """ 
    Specific logic for Document/eBook generation. 
    Checks for 'Pedagogical Integrity' and 'Hyme' words if it's a doc request. 
    This implies the context needs to know if it's a doc request. 
    We can infer from context (maybe an extended field). 
    """ 
    rule_id = "R_DOC_001" 
    description = "Ensures pedagogical safety & no hype." 

    def evaluate(self, context: DecisionContext, safety_level: SafetyLevel) -> Tuple[bool, str, DecisionReasonCode]: 
        # Only apply if we have pedagogical signals 
        if context.pedagogical_integrity_score is None: 
            return True, "Not a document request.", DecisionReasonCode.ALL_CHECKS_PASSED 
            
        # 1. Semantic Wall Check (Forex vs Indices) 
        # This is usually done upstream, but we check the flag/score here. 
        # Prompt: "Reject any document that contains FOREX terminology in an INDICES manual." 
        # We assume upstream agents calculated the 'pedagogical_integrity_score'. 
        if context.pedagogical_integrity_score < 0.9: # arbitrary high bar 
            return False, "Pedagogical Integrity Score too low (Mixed Terminology?).", DecisionReasonCode.PEDAGOGICAL_VIOLATION 
            
        # 2. Hype Check 
        # "Guaranteed", "Always" -> check claims 
        bad_words = ["guaranteed", "always", "100%", "risk-free"] 
        for claim in context.document_claims: 
            for bad in bad_words: 
                if bad in claim.lower(): 
                    return False, f"Hype detected in claim: '{claim}'", DecisionReasonCode.PEDAGOGICAL_VIOLATION 
                    
        return True, "Document content passed integrity.", DecisionReasonCode.ALL_CHECKS_PASSED 
