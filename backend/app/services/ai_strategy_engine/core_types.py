from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime

# --- Enums (Market/Logic Types) ---
class Trend(Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"

class ArrayType(Enum):
    FVG = "Fair Value Gap"
    ORDER_BLOCK = "Order Block"
    BREAKER = "Breaker"
    LIQUIDITY_POOL = "Liquidity Pool"
    SWING_POINT = "Swing Point"

class LogicType(Enum):
    ENTRY = "ENTRY"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"
    INVALIDATION = "INVALIDATION"
    CONTEXT = "CONTEXT"

# --- Normalized Strategy Structures ---
@dataclass
class LogicBlock:
    """Represents a single atomic rule (e.g., 'Price < FLOD')."""
    id: str
    logic_type: LogicType
    condition: str  # The executable condition string
    required_array: Optional[ArrayType] = None
    parameters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class NormalizedStrategy:
    """A strategy stripped of narrative, ready for evaluation."""
    strategy_id: str
    original_name: str
    bias: Trend = Trend.NEUTRAL
    
    # The Logic
    context_rules: List[LogicBlock] = field(default_factory=list)      # e.g., Time filters, Trend
    trigger_rules: List[LogicBlock] = field(default_factory=list)      # e.g., Displacement, Sweep
    entry_rules: List[LogicBlock] = field(default_factory=list)        # e.g., Retrace to FVG
    invalidation_rules: List[LogicBlock] = field(default_factory=list) # e.g., Close beyond LLOD
    
    # Metadata
    source_file: str = ""
    is_active: bool = True
    deduplication_id: str = "" # Hash of the logic blocks

@dataclass
class EvaluationResult:
    """The Output of AI #2."""
    strategy_id: str
    timestamp: datetime
    is_applicable: bool
    confidence_score: float # 0.0 to 100.0
    active_conflicts: List[str] # List of conflicting strategy IDs
    confluence_count: int
    notes: List[str]
