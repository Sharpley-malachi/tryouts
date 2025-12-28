import logging 
from typing import Dict, List, Optional 
from datetime import datetime, timezone, timedelta 

from ..core.slsm_schema import StrategyState, StrategyDNA, MarketRegime 
# We assume we might need DAE integration, but SLSM mainly manages state that DAE reads. 

logger = logging.getLogger("SLSM") 
logger.setLevel(logging.INFO) 

class SLSM_Governor: 
    """ 
    The Strategy Lifecycle State Machine (SLSM) Engine. 
    Governs the evolution, degradation, and retirement of strategies. 
    """ 
    def __init__(self): 
        self.strategy_registry: Dict[str, StrategyDNA] = {} 
        # Configuration for transitions 
        self.min_samples_for_promotion = 30 
        self.min_win_rate_active = 0.55 
        self.max_consecutive_losses = 3 
        self.confidence_half_life_days = 7 

    def register_strategy(self, dna: StrategyDNA): 
        """ 
        Ingests a new strategy into the ecosystem. Starts in DORMANT or SHADOW. 
        """ 
        if dna.strategy_id in self.strategy_registry: 
            logger.warning(f"Strategy {dna.strategy_id} already exists. Updating ??") 
        
        # New strategies often start in SHADOW_MODE if they claim to be ready 
        if dna.state == StrategyState.DORMANT: 
            # Check if it should move to Shadow 
            dna.state = StrategyState.SHADOW_MODE 
            
        self.strategy_registry[dna.strategy_id] = dna 
        logger.info(f"Registered Strategy {dna.strategy_id} in state {dna.state.value}") 

    def evaluate_transitions(self, strategy_id: str, current_market_regime: MarketRegime) -> StrategyState: 
        """ 
        The Core Logic: Determines if a strategy moves up or down the hierarchy. 
        Must be called periodically or after trade outcomes. 
        """ 
        dna = self.strategy_registry.get(strategy_id) 
        if not dna: 
            raise ValueError(f"Strategy {strategy_id} not found in registry.") 

        old_state = dna.state 
        
        # 0. Global Decay Check (Time-based) 
        self._apply_confidence_decay(dna) 

        # 1. Regime Mismatch Check (Immediate Suspension/Sleep) 
        if current_market_regime not in dna.regime_tags: 
            # If active, suspend it. If shadow, just wait? 
            if dna.state in [StrategyState.ACTIVE, StrategyState.PROBATION, StrategyState.EXPERIMENTAL]: 
                logger.info(f"Regime Mismatch for {dna.strategy_id}. {current_market_regime} not in {dna.regime_tags}. Suspending.") 
                return self._transition(dna, StrategyState.SUSPENDED, "Regime Mismatch") 
        elif dna.state == StrategyState.SUSPENDED: 
            # Try to unsuspended if regime matches now 
             if current_market_regime in dna.regime_tags: 
                 # Return to previous state logic (simplified: go to Probation/Degraded to re-prove?) 
                 # Let's go to DEGRADED for a 'warm up' or back to PROBATION. 
                 return self._transition(dna, StrategyState.DEGRADED, "Regime Match - Waking up") 

        # 2. Failure Checks (Quarantine/Degrade) 
        if self._detect_streak_failure(dna): 
             if dna.state == StrategyState.ACTIVE: 
                 return self._transition(dna, StrategyState.QUARANTINE, "Consecutive Loss Threshold Hit") 
             elif dna.state in [StrategyState.PROBATION, StrategyState.EXPERIMENTAL]: 
                 return self._transition(dna, StrategyState.DEGRADED, "Performance Dip in Evaluation") 

        # 3. Promotion Logic (Upward Mobility) 
        merit_score = self._calculate_merit_score(dna) 
        
        # Shadow -> Probation 
        if dna.state == StrategyState.SHADOW_MODE: 
            if merit_score > 0.80 and len(dna.win_loss_history) > 10: 
                return self._transition(dna, StrategyState.EXPERIMENTAL, "Passed Shadow Phase") 
        
        # Experimental -> Probation 
        if dna.state == StrategyState.EXPERIMENTAL: 
             if merit_score > 0.75 and len(dna.win_loss_history) > 20: 
                 return self._transition(dna, StrategyState.PROBATION, "Passed Experimental Phase") 

        # Probation -> Active 
        if dna.state == StrategyState.PROBATION: 
            if merit_score > 0.70 and len(dna.win_loss_history) >= self.min_samples_for_promotion: 
                 # Validate Win Rate 
                 if dna.historical_win_rate >= self.min_win_rate_active: 
                     return self._transition(dna, StrategyState.ACTIVE, "Fully Promoted to ACTIVE") 

        return dna.state 

    def report_outcome(self, strategy_id: str, outcome_win: bool, pnl: float): 
        """ 
        Feeds performance data back into the DNA. 
        """ 
        dna = self.strategy_registry.get(strategy_id) 
        if not dna: 
             return 
        
        # Update History 
        dna.win_loss_history.append(1 if outcome_win else 0) 
        if outcome_win: 
            dna.consecutive_losses = 0 
            # Boost confidence slightly 
            dna.confidence_score = min(1.0, dna.confidence_score + 0.05) 
        else: 
            dna.consecutive_losses += 1 
            # Hit confidence 
            dna.confidence_score = max(0.0, dna.confidence_score - 0.10) 
            
        # Re-calc win rate 
        total = len(dna.win_loss_history) 
        wins = sum(dna.win_loss_history) 
        dna.historical_win_rate = wins / total if total > 0 else 0.0 
        
        dna.last_active_timestamp = datetime.now(timezone.utc) 
        dna.last_evaluation_timestamp = datetime.now(timezone.utc) 

    def _calculate_merit_score(self, dna: StrategyDNA) -> float: 
        """ 
        Composite score logic. 
        """ 
        # Base confidence 
        score = dna.confidence_score 
        
        # Penalty for low sample size if active? 
        # Bonus for recent wins? 
        return score 

    def _detect_streak_failure(self, dna: StrategyDNA) -> bool: 
        return dna.consecutive_losses >= self.max_consecutive_losses 

    def _apply_confidence_decay(self, dna: StrategyDNA): 
        """ 
        If not active for X days, decay confidence. 
        """ 
        if not dna.last_active_timestamp: 
            return 
            
        delta = datetime.now(timezone.utc) - dna.last_active_timestamp 
        if delta.days > 2: 
            decay = 0.01 * delta.days 
            dna.confidence_score = max(0.1, dna.confidence_score - decay) 

    def _transition(self, dna: StrategyDNA, new_state: StrategyState, reason: str) -> StrategyState: 
        if dna.state == new_state: 
            return dna.state 
            
        logger.info(f"TRANSITION: {dna.strategy_id} | {dna.state.value} -> {new_state.value} | Reason: {reason}") 
        dna.state = new_state 
        return new_state 

# Singleton Instance 
slsm_engine = SLSM_Governor() 
