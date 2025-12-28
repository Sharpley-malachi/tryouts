from core_types import NormalizedStrategy, LogicBlock, Trend

class ContextEvaluator:
    def __init__(self):
        pass

    def check_market_conditions(self, strategy: NormalizedStrategy, market_state: dict) -> float:
        """
        Returns a probability score (0.0 - 1.0) based on context alignment.
        """
        score = 1.0
        penalties = 0.0
        
        # 1. Check Trend Alignment (Rule: Layer 2 Directional Bias)
        trend_rule = next((r for r in strategy.context_rules if r.id == "CTX_TREND_STRUCT"), None)
        if trend_rule:
             # Logic: If strategy requires Trend, but market is Mixed/Range
            if market_state['htf_trend'] != market_state['ltf_trend']:
                 # The Arjo "Low Probability" definition: Ambiguity
                penalties += 0.5

        # 2. Check Time Filters (Rule: Environment Filters)
        time_rule = next((r for r in strategy.context_rules if r.id == "ENV_TIME"), None)
        if time_rule:
            current_hour = market_state['current_time'].hour
            # Simple Killzone Logic (London 2-5, NY 8-11)
            is_killzone = (2 <= current_hour <= 5) or (8 <= current_hour <= 11)
            if not is_killzone:
                penalties += 0.8 # Heavy penalty for trading outside killzones (Arjo Logic)
        
        final_score = max(0.0, score - penalties)
        return final_score
