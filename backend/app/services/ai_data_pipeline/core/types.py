from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import datetime

class Timeframe(Enum):
    M15 = "15m"
    H1 = "1H" 
    H4 = "4H"
    DAILY = "D"
    WEEKLY = "W"
    MONTHLY = "M"

@dataclass
class MarketCandle:
    timestamp: datetime.datetime
    open: float
    high: float
    low: float
    close: float
    timeframe: str 
    source_batch_id: str

@dataclass
class PredictionSnapshot:
    prediction_id: str
    correlation_id: str
    timestamp: datetime.datetime
    target_symbol: str
    timeframe: str
    strategy_bias: str
    market_state_snapshot: Dict[str, Any]
    ai_confidence: float
    status: str = "PENDING"

@dataclass
class FeedbackRecord:
    prediction_id: str
    outcome_candles: List[MarketCandle]
    result: str # "WIN", "LOSS", "BE"
    notes: str
