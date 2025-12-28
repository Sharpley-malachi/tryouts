from enum import Enum 
from typing import List, Dict, Optional, Any 
from dataclasses import dataclass, field 
from datetime import datetime, timezone 

class StrategyState(str, Enum): 
    DORMANT = "DORMANT" 
    SHADOW_MODE = "SHADOW_MODE"       # Internal testing, invisible to user 
    EXPERIMENTAL = "EXPERIMENTAL"     # Limited exposure, visible 
    PROBATION = "PROBATION"           # Monitoring for consistency 
    ACTIVE = "ACTIVE"                 # Full permissions 
    QUARANTINE = "QUARANTINE"         # Suspicion / Failure investigation 
    DEGRADED = "DEGRADED"             # Performance decay or cooling off 
    SUSPENDED = "SUSPENDED"           # Temporarily disabled (e.g. regime mismatch) 
    RETIRED = "RETIRED"               # Permanently stopped 
    ARCHIVED = "ARCHIVED"             # Historical reference only 

class MarketRegime(str, Enum): 
    TRENDING_HIGH_VOL = "TRENDING_HIGH_VOL" 
    TRENDING_LOW_VOL = "TRENDING_LOW_VOL" 
    RANGING_HIGH_VOL = "RANGING_HIGH_VOL" 
    RANGING_LOW_VOL = "RANGING_LOW_VOL" 
    UNCERTAIN = "UNCERTAIN" 

@dataclass 
class StrategyDNA: 
    """ 
    Versioned DNA Object representing a trading strategy. 
    """ 
    strategy_id: str 
    version: str 
    origin: str  # human | mined | hybrid 
    regime_tags: List[MarketRegime] 
    
    # State tracking 
    state: StrategyState = StrategyState.DORMANT 
    creation_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc)) 
    last_evaluation_timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc)) 
    
    # Lineage 
    parent_id: Optional[str] = None 
    lineage_reference: Dict[str, Any] = field(default_factory=dict) # Links to videos, data sources 
    
    # Performance Stats (Simplified for DNA) 
    confidence_score: float = 0.5 
    historical_win_rate: float = 0.0 
    win_loss_history: List[int] = field(default_factory=list) # 1 for win, 0 for loss 
    consecutive_losses: int = 0 
    
    # Time specific 
    timeframes: List[str] = field(default_factory=list) 
    last_active_timestamp: Optional[datetime] = None 
    
    def to_dict(self) -> Dict[str, Any]: 
        return { 
            "id": self.strategy_id, 
            "version": self.version, 
            "state": self.state.value, 
            "tags": [t.value for t in self.regime_tags], 
            "confidence": self.confidence_score, 
            "win_rate": self.historical_win_rate 
        } 
