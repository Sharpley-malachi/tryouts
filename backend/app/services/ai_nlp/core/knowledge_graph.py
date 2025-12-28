class KnowledgeGraph:
    def __init__(self):
        # Tracks concepts explained to the user
        self.mastered_concepts = set()
        self.dependencies = {
            "Liquidity_Sweep": ["Liquidity_Basics", "Swing_Points"],
            "FVG_Entry": ["Imbalance_Basics", "Market_Structure"],
            "PD_Array_Targeting": ["Premium_Discount_Arrays"],
            "Masking_Study": ["Candlestick_Anatomy", "Predictive_Bias"],
            "Archetype_Discovery": ["Pattern_Recognition_Basics"]
        }

    def get_prerequisites(self, concept):
        needed = self.dependencies.get(concept, [])
        return [p for p in needed if p not in self.mastered_concepts]

    def mark_as_taught(self, concept):
        self.mastered_concepts.add(concept)
