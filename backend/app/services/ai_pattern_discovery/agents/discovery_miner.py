import hashlib
import json
import os

class DiscoveryMinerAgent:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.memory_file = os.path.join(data_dir, "pattern_memory.json")
        self.pattern_memory = self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_memory(self):
        with open(self.memory_file, 'w') as f:
            json.dump(self.pattern_memory, f, indent=2)

    def analyze_target_journey(self, entry_point, target_price, candles_during_journey):
        """
        Analyzes how price moved towards a PD Array.
        Identifies if it was a 'Direct Shot' or 'Staircase'.
        """
        journey_type = "Direct"
        counter_candle_count = 0
        
        for candle in candles_during_journey:
            # Check for candles moving AGAINST the target
            if self._is_counter_move(candle, target_price):
                counter_candle_count += 1
        
        # If counter-candles exist but target is still hit:
        # This is a 'Resilient Trend' pattern.
        resilience_score = 1.0
        if len(candles_during_journey) > 0:
            resilience_score = 1 - (counter_candle_count / len(candles_during_journey))
            
        if counter_candle_count > 0:
            journey_type = "Staircase_Expansion"
            
        return {
            "journey_type": journey_type,
            "resilience_score": resilience_score,
            "late_entry_viability": self._check_mid_move_entry(candles_during_journey)
        }

    def _is_counter_move(self, candle, target):
        # candle [O, H, L, C, V]
        close = candle[3]
        open_p = candle[0]
        # If target is above, and close < open (Red), it's counter
        if target > open_p and close < open_p: return True
        # If target is below, and close > open (Green), it's counter
        if target < open_p and close > open_p: return True
        return False

    def _check_mid_move_entry(self, candles):
        # Placeholder: Did price offer a pullback > 50% of previous candle?
        return "Possible"

    def discover_new_pattern(self, candle_structure):
        """
        Generates a unique ID and Name for a discovered shape.
        candle_structure: List of candles (e.g. 5 candles)
        """
        # Create a simplified string signature: "Green-Red-Green-BigBody-SmallWick"
        # For valid hashing, we use values normalized
        signature = str(candle_structure) 
        pattern_hash = hashlib.md5(signature.encode()).hexdigest()[:8]
        
        if pattern_hash not in self.pattern_memory:
            name = f"ARCHETYP_{pattern_hash.upper()}"
            self.pattern_memory[pattern_hash] = {
                "name": name,
                "frequency": 1,
                "description": "Newly discovered price sequence anomaly.",
                "first_seen": "Now",
                "structure": str(candle_structure)[:50] + "..."
            }
        else:
            self.pattern_memory[pattern_hash]["frequency"] += 1
            
        self._save_memory()
        return self.pattern_memory[pattern_hash]
