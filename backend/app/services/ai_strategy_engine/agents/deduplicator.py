import hashlib
from typing import List, Dict
from core_types import NormalizedStrategy

class DeduplicationAgent:
    def __init__(self):
        self.unique_logic_hashes = {}
        
    def process(self, strategies: List[NormalizedStrategy]) -> List[NormalizedStrategy]:
        print("\n--- Agent: De-Duplicator ---")
        cleaned_list = []
        
        for strat in strategies:
            # Create a fingerprint of the logic only (ignoring the name)
            logic_signature = ""
            
            # Combine all rules into a string
            all_rules = strat.context_rules + strat.trigger_rules + strat.entry_rules
            for rule in sorted(all_rules, key=lambda x: x.id):
                logic_signature += f"{rule.id}|{rule.condition}|"
            
            # Hash it
            strat_hash = hashlib.md5(logic_signature.encode()).hexdigest()
            strat.deduplication_id = strat_hash
            
            if strat_hash in self.unique_logic_hashes:
                original = self.unique_logic_hashes[strat_hash]
                print(f"[DUPLICATE DETECTED] Strategy '{strat.original_name}' is logic-identical to '{original}'. Merging...")
                # We do not add it to cleaned_list, effectively removing the duplicate logic
            else:
                self.unique_logic_hashes[strat_hash] = strat.original_name
                cleaned_list.append(strat)
                
        return cleaned_list
