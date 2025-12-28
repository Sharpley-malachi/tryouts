from enum import Enum
from .core.bus import OrchestrationBus
from .core.sentinel import HindsightSentinel
from app.agents.decision_engine import DecisionAuthorizationEngine
from app.core.dae_schema import SafetyLevel
from app.services.ai_strategy_engine.agents.slsm_governor import slsm_engine, SLSM_Governor
from app.services.ai_strategy_engine.core.truth_ledger import truth_ledger, LedgerEventType

class SystemState(Enum):
    INGESTION = 1   # AI #1 & Firebase
    RESEARCH = 2    # AI #3 (Discovery) & AI #2 (Testing)
    PRODUCTION = 3  # AI #4 & AI #5 (Prediction/Explanation)
    PUBLICATION = 4 # AI #6 (Crystallizing E-Books)
    DORMANT = 5     # Idle/Monitoring

class TheGeneral:
    def __init__(self):
        self.state = SystemState.DORMANT
        self.timestamp_lock = None # Global Sync Clock
        self.confidence_history = []
        self.version_history = [] # For Rollback Protocol
        
        self.bus = OrchestrationBus()
        self.sentinel = HindsightSentinel()
        self.dae = DecisionAuthorizationEngine(SafetyLevel.CONSERVATIVE)
        self.slsm = slsm_engine # Using the singleton or instance logic
        self.ledger = truth_ledger

    def set_system_state(self, new_state_name: str):
        """
        Transitions the system between operational modes.
        Enforces clean handoffs.
        """
        try:
            # Map string to Enum
            new_state = SystemState[new_state_name.upper()]
        except KeyError:
             print(f"Invalid State: {new_state_name}")
             return {"status": "error", "message": "Invalid State"}

        print(f"--- SYSTEM COMMAND: Transitioning to {new_state.name} ---")
        self.state = new_state
        
        # Notify all agents via the Bus
        self.bus.broadcast_state_change(new_state.name)
        
        # Ledger Record
        self.ledger.record_event(LedgerEventType.STRATEGY_STATE_CHANGED, {
            "action": "SYSTEM_TRANSITION",
            "new_state": new_state.name
        })
        
        return {"status": "success", "new_state": new_state.name}

    def register_agent_heartbeat(self, agent_id, confidence):
        """
        Agents call this to report their status.
        """
        self.bus.update_status(agent_id, "ACTIVE", confidence)
        return {"status": "acknowledged"}

    def request_authorization(self, context):
        """
        Routes a request through the Decision Authorization Engine.
        """
        decision = self.dae.authorize(context)
        
        # Ledger Record
        self.ledger.record_event(LedgerEventType.DAE_INTERLOCK, {
            "status": decision.authorization_status,
            "reason": decision.decision_reason_human,
            "hash": decision.audit_hash
        })
        
        return decision

    def evaluate_strategy_lifecycle(self, strategy_id, market_regime):
        """
        Triggers a lifecycle review for a strategy.
        """
        return self.slsm.evaluate_transitions(strategy_id, market_regime)

    def register_new_strategy(self, dna):
        """
         onboards a new strategy.
        """
        self.slsm.register_strategy(dna)

    def get_system_health(self):
        """
        Returns Dashboard Telemetry.
        """
        # Calculate Weighted Confidence
        total = 0
        count = 0
        for data in self.bus.registry.values():
            total += data['confidence']
            count += 1
        avg_conf = total / count if count > 0 else 0
        
        return {
            "mode": self.state.name,
            "weighted_confidence": avg_conf,
            "sync_lock": "SYNCED" if self.timestamp_lock is None else "LOCKED",
            "registry": self.bus.registry
        }

    def emergency_shutdown(self):
        self.state = SystemState.DORMANT
        print("EMERGENCY SHUTDOWN INITIATED")
        return {"status": "shutdown"}

# Singleton is now instantiated in dependencies.py
