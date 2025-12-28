from core_types import NormalizedStrategy, LogicBlock, LogicType, ArrayType, Trend

class NormalizationAgent:
    def __init__(self):
        pass

    def normalize(self, raw_data: dict) -> NormalizedStrategy:
        """
        Converts raw JSON into a NormalizedStrategy object.
        Strips narrative, keeps logic.
        """
        strategy = NormalizedStrategy(
            strategy_id=raw_data['id'],
            original_name=raw_data['name'],
            bias=Trend.NEUTRAL 
        )
        
        logic = raw_data.get('layer_4_logic', {})
        env = raw_data.get('environment_filters', {})
        
        # 1. Parse Context (The Setup)
        if "Context" in logic:
            txt = logic["Context"].lower()
            if "sweep" in txt:
                strategy.context_rules.append(LogicBlock(
                    id="CTX_SWEEP", logic_type=LogicType.CONTEXT,
                    condition="price_sweeps_swing_point", required_array=ArrayType.LIQUIDITY_POOL
                ))
            elif "trend" in txt or "ith" in txt:
                 strategy.context_rules.append(LogicBlock(
                    id="CTX_TREND_STRUCT", logic_type=LogicType.CONTEXT,
                    condition="check_market_structure_trend"
                ))
            elif "pd array" in txt:
                 strategy.context_rules.append(LogicBlock(
                    id="CTX_PD_FLOW", logic_type=LogicType.CONTEXT,
                    condition="price_approaching_pd_array"
                ))
            elif "opposing array" in txt:
                 strategy.context_rules.append(LogicBlock(
                    id="CTX_RESISTANCE_HIT", logic_type=LogicType.CONTEXT,
                     condition="hit_unmitigated_opposing"
                 ))

        # 2. Parse Trigger (The Event)
        if "Trigger" in logic:
            txt = logic["Trigger"].lower()
            if "fvg" in txt:
                # Differentiate based on context
                if "create" in txt or "formation" in txt:
                     strategy.trigger_rules.append(LogicBlock(
                        id="TRIG_FVG_CREATION", logic_type=LogicType.CONTEXT,
                        condition="formation_new_fvg", required_array=ArrayType.FVG
                    ))
                else:
                    strategy.trigger_rules.append(LogicBlock(
                        id="TRIG_FVG_RETRACE", logic_type=LogicType.CONTEXT,
                        condition="retrace_to_fvg", required_array=ArrayType.FVG
                    ))
            elif "break" in txt:
                 strategy.trigger_rules.append(LogicBlock(
                    id="TRIG_BOS", logic_type=LogicType.CONTEXT,
                    condition="break_of_structure"
                ))

        # 3. Parse Environment Filters (Time, etc)
        # STRICT RULE: Ignore Psychology, focus on Time/News exclusion
        if "Time" in env:
            strategy.context_rules.append(LogicBlock(
                id="ENV_TIME", logic_type=LogicType.CONTEXT,
                condition="check_killzone_or_news", parameters={"raw_rule": env["Time"]}
            ))
            
        return strategy
