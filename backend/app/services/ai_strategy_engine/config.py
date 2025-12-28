from dataclasses import dataclass

@dataclass
class EngineConfig:
    KNOWLEDGE_BASE_PATH: str = "knowledge_base"
    STRATEGIES_PATH: str = "knowledge_base/strategies"
    
    # Confidence Thresholds
    MIN_CONFIDENCE_THRESHOLD: float = 60.0
    CONFLICT_PENALTY: float = 0.5
    CONFLUENCE_BOOST: float = 10.0
    
    # Market Constants
    KILLZONE_LONDON = [2, 3, 4, 5]
    KILLZONE_NY = [8, 9, 10, 11]

config = EngineConfig()
