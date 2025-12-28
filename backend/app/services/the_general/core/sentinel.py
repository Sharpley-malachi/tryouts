class HindsightSentinel:
    def verify_temporal_integrity(self, visual_state, current_anchor):
        """
        THE HINDSIGHT SENTINEL: 
        Ensures AI #5 (Visuals) never shows a candle timestamp 
        ahead of the current processing 'anchor'.
        """
        if not visual_state or not current_anchor:
            return True # Pass contextually
            
        rendered_timestamp = visual_state.get('last_visible_candle_idx', 0)
        
        if rendered_timestamp > current_anchor: 
            print("SECURITY VIOLATION: Hindsight Leak Detected!")
            return False
        return True

    def check_logic_drift(self, strategy_output, discovery_output):
        """
        Detects if AI #2 and AI #3 are contradicting each other.
        """
        if not strategy_output or not discovery_output:
            return "Stable"

        # Mock Logic Check
        strat_bias = strategy_output.get('bias', 'NEUTRAL')
        disc_bias = discovery_output.get('bias', 'NEUTRAL')
        
        if strat_bias != disc_bias and strat_bias != 'NEUTRAL' and disc_bias != 'NEUTRAL':
             return "CONFLICT_DETECTED"
             
        return "Stable"
