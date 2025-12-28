class FactChecker:
    def verify_claim(self, claim_text, raw_stats):
        """
        Audits sentences for mathematical honesty.
        """
        # Dictionary of 'Power Words' that require high statistical proof
        strict_thresholds = {
            "high probability": 0.75, # Adjusted to ratio (0.75) if stats are ratio, or 75.0 if percentage. Assuming 0-1 or 0-100 logic.
            "consistent": 0.70,
            "reliable": 0.65,
            "guaranteed": 100.0  # Will always fail, forcing a rewrite
        }
        
        # Normalize stats (assuming input might be dict)
        win_rate = raw_stats.get('win_rate', 0)
        # Handle 0-1 vs 0-100 confusion safely
        if win_rate <= 1.0: win_rate *= 100

        for word, threshold in strict_thresholds.items():
            if word in claim_text.lower():
                if win_rate < (threshold if threshold > 1 else threshold * 100):
                    return False, f"Confidence Mismatch: '{word}' requires {threshold}%, got {win_rate}%"
        
        return True, "Verified"

    def audit_visual_alignment(self, text, chart_metadata):
        """
        Ensures the text matches the visual (e.g., 'Bullish' text vs 'Bearish' chart).
        """
        text_lower = text.lower()
        bias = chart_metadata.get('bias', 'NEUTRAL').lower()
        
        if "bullish" in text_lower and bias == "bearish":
            return False, "Visual/Narrative Conflict: Text says Bullish, Chart is Bearish"
        if "bearish" in text_lower and bias == "bullish":
            return False, "Visual/Narrative Conflict: Text says Bearish, Chart is Bullish"
            
        return True, "Aligned"
