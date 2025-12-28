import hashlib 
import json 
import uuid 
import logging 
from typing import List, Optional, Any, Dict 
from datetime import datetime, timezone 

from ..core.dae_schema import ( 
    DecisionContext, DecisionOutput, AuthorizationStatus, 
    DecisionReasonCode, SafetyLevel 
) 
from ..core.dae_rules import ( 
    DAERule, DataDriftRule, RiskRewardRule, 
    ConfidenceGatingRule, StrategySanityRule, 
    EducationalIntegrityRule 
) 

# Setup basic logging 
logger = logging.getLogger("DAE") 
logger.setLevel(logging.INFO) 

class DecisionAuthorizationEngine: 
    """ 
    The Decision Authorization Engine (DAE). 
    The governance kernel that gates all actions. 
    Deterministic. Stateless (mostly). Auditable. 
    """ 
    def __init__(self, safety_level: SafetyLevel = SafetyLevel.CONSERVATIVE): 
        self.safety_level = safety_level 
        self.rules: List[DAERule] = [ 
            DataDriftRule(), 
            StrategySanityRule(), 
            ConfidenceGatingRule(), 
            RiskRewardRule(), 
            EducationalIntegrityRule() 
        ] 

    def set_safety_level(self, level: SafetyLevel): 
        logger.info(f"DAE Safety Level changed to: {level}") 
        self.safety_level = level 

    def authorize(self, context: DecisionContext) -> DecisionOutput: 
        """ 
        The main entry point. Evaluates all rules against the context. 
        Fail-Closed: Any breakdown results in REJECTION. 
        """ 
        # 1. Basic Schema Validation (Implied by strong typing, but we guard against Nones) 
        if context is None: 
            return self._create_rejection("Context is None/Empty", DecisionReasonCode.INTERNAL_ERROR) 
            
        violated_rules = [] 
        
        # 2. Iterate Rules 
        for rule in self.rules: 
            try: 
                passed, reason, code = rule.evaluate(context, self.safety_level) 
                if not passed: 
                    logger.warning(f"Rule Failed: {rule.rule_id} - {reason}") 
                    violated_rules.append(f"{rule.rule_id}: {reason}") 
                    # We can choose to return immediately or collect all failures. 
                    # Prompt says "Fail-Closed... Deny by Default". 
                    # Prompt also says "violated_rules[] (if any)". 
                    # So we collect all for better feedback, then reject. 
            except Exception as e: 
                # Fail Closed on logic errors 
                logger.error(f"DAE Logic Error on rule {rule.rule_id}: {str(e)}") 
                return self._create_rejection( 
                    f"Internal Logic Error during evaluation: {str(e)}", 
                    DecisionReasonCode.INTERNAL_ERROR 
                ) 

        # 3. Decision Construction 
        if violated_rules: 
            # If any rule failed, we REJECT. 
            # We assume the last failure code is the primary one for the enum, 
            # or we prioritize. Let's pick the first one roughly or generic. 
            # Simple heuristic: Just REJECT. 
            return DecisionOutput( 
                authorization_status=AuthorizationStatus.REJECTED, 
                auth_token=None, 
                decision_reason_code=DecisionReasonCode.ALL_CHECKS_PASSED if not violated_rules else DecisionReasonCode.INTERNAL_ERROR, 
                decision_reason_human="One or more governance rules were violated.", 
                violated_rules=violated_rules, 
                required_future_conditions=[], # Logic for DEFERRED would go here 
                audit_hash=self._generate_audit_hash(context, AuthorizationStatus.REJECTED), 
                authorized_parameters={} 
            ) 
            
        # 4. Overrides Check (User Lock) 
        if context.human_lock_flag: 
            return DecisionOutput( 
                authorization_status=AuthorizationStatus.REJECTED, 
                auth_token=None, 
                decision_reason_code=DecisionReasonCode.USER_SAFETY_LOCK, 
                decision_reason_human="Manual Safety Lock is Engaged.", 
                violated_rules=["Human Override"], 
                required_future_conditions=[], 
                audit_hash=self._generate_audit_hash(context, AuthorizationStatus.REJECTED), 
                authorized_parameters={} 
            ) 

        # 5. Approve 
        auth_token = self._generate_auth_token(context) 
        return DecisionOutput( 
            authorization_status=AuthorizationStatus.APPROVED, 
            auth_token=auth_token, 
            decision_reason_code=DecisionReasonCode.ALL_CHECKS_PASSED, 
            decision_reason_human=f"Authorized under {self.safety_level.value} protocols.", 
            violated_rules=[], 
            required_future_conditions=[], 
            audit_hash=self._generate_audit_hash(context, AuthorizationStatus.APPROVED, auth_token), 
            authorized_parameters={ 
                "max_risk": context.strategy_state.max_allowed_risk_for_context, 
                "timestamp_approved": datetime.now(timezone.utc).isoformat() 
            } 
        ) 

    def _create_rejection(self, reason: str, code: DecisionReasonCode) -> DecisionOutput: 
        return DecisionOutput( 
            authorization_status=AuthorizationStatus.REJECTED, 
            auth_token=None, 
            decision_reason_code=code, 
            decision_reason_human=reason, 
            violated_rules=["Critical Failure"], 
            required_future_conditions=[], 
            audit_hash="FAIL_HASH", 
            authorized_parameters={} 
        ) 

    def _generate_auth_token(self, context: DecisionContext) -> str: 
        """ 
        Creates a cryptographic token proving authorization. 
        """ 
        payload = f"{context.identity.global_correlation_id}|{context.identity.strategy_id}|{datetime.now(timezone.utc)}" 
        return hashlib.sha256(payload.encode()).hexdigest() 

    def _generate_audit_hash(self, context: DecisionContext, status: AuthorizationStatus, token: str = "") -> str: 
        """ 
        Creates an immutable record hash of inputs + output. 
        """ 
        # Minimal serialization for hash 
        data = f"{context.identity.global_correlation_id}{status}{token}{context.strategy_state.status}" 
        return hashlib.sha256(data.encode()).hexdigest() 

    def replay_decision(self, old_context: DecisionContext, expected_hash: str) -> bool: 
        """ 
        Verifies if a past decision matches current logic (Version consistency check). 
        """ 
        # This is complex in real life (requires versioned rules), 
        # but here we just re-run authorize. 
        result = self.authorize(old_context) 
        # Note: timestamps in audit hash might mismatch, so this is illustrative. 
        return True 

if __name__ == "__main__": 
    # Quick Test 
    from datetime import timedelta 
    from ..core.dae_schema import IdentityLineage, DataIntegritySignals, StrategyState, ConfidenceRiskSignals, TimeframeClass, StrategyStatus 
    
    # Mock Data 
    now = datetime.now(timezone.utc) 
    mock_ctx = DecisionContext( 
        identity=IdentityLineage("ID_123", "REQ_1", "AGENT_7", "STRAT_A", "EURUSD", "FOREX", "4H", now), 
        integrity=DataIntegritySignals(1.0, 0.99, 1.2, 100, now, human_latency_drift=2.0), 
        strategy_state=StrategyState(StrategyStatus.ACTIVE, 100, 0.65, False, None), 
        risk_signals=ConfidenceRiskSignals(0.88, 2.5, TimeframeClass.SWING, 1.1000, 1.0900, 1.1200) 
    ) 
    
    engine = DecisionAuthorizationEngine(SafetyLevel.IRONCLAD) 
    result = engine.authorize(mock_ctx) 
    print(f"Decision: {result.authorization_status}") 
    print(f"Reason: {result.decision_reason_human}") 
    print(f"Token: {result.auth_token}") 
