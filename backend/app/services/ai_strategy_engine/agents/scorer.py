from typing import List, Dict
from core_types import NormalizedStrategy, EvaluationResult, Trend
from datetime import datetime

class ScorerAgent:
    def __init__(self):
        pass

    def evaluate_batch(self, strategies: List[NormalizedStrategy], context_scores: Dict[str, float]) -> List[EvaluationResult]:
        results = []
        
        # 1. Determine Bias per Strategy AND Group them
        # In a real engine, we'd run the actual 'Trigger' logic against price data here.
        active_biases = {"BULLISH": [], "BEARISH": []}
        
        for strat in strategies:
            score = context_scores.get(strat.strategy_id, 0.0)
            is_applicable = score > 0.6 # Threshold for applicability
            
            # Simulated Bias determination based on logic blocks
            # Dictionary mapping known logic block IDs to likely bias
            current_bias_str = "BULLISH" # Default placeholder for the demo
            
            # Simple heuristic: If trigger says 'Opposing FVG' and Context is 'Resistance', likely Short
            for rule in strat.context_rules:
                if "RESISTANCE" in rule.id:
                    current_bias_str = "BEARISH"
            
            if is_applicable:
                active_biases[current_bias_str].append(strat.strategy_id)
            
            results.append(EvaluationResult(
                strategy_id=strat.strategy_id,
                timestamp=datetime.now(),
                is_applicable=is_applicable,
                confidence_score=score * 100,
                active_conflicts=[], # Filled in next step
                confluence_count=0,
                notes=[f"Logic Score: {score:.2f}, Bias: {current_bias_str}"]
            ))

        # 2. Conflict Detection
        # If we have applicable strategies in both Bullish and Bearish buckets, we have a conflict.
        conflict_exists = len(active_biases["BULLISH"]) > 0 and len(active_biases["BEARISH"]) > 0
        
        for res in results:
            if res.is_applicable:
                # Find my bias
                my_bias = "BULLISH" if "BULLISH" in res.notes[0] else "BEARISH"
                opposing_bias = "BEARISH" if my_bias == "BULLISH" else "BULLISH"
                
                # Check Conflict
                if conflict_exists and len(active_biases[opposing_bias]) > 0:
                    res.active_conflicts = active_biases[opposing_bias]
                    res.notes.append("WARNING: Market Ambiguity. Conflicting signals detected.")
                    res.confidence_score *= 0.5 # Degrade score in conflict

                # Check Confluence (Other strategies agreeing)
                res.confluence_count = len(active_biases[my_bias]) - 1 # Minus self
                if res.confluence_count > 0:
                    res.confidence_score += (res.confluence_count * 10) # Boost score
                
                res.confidence_score = min(100.0, res.confidence_score)
                
        return results
